"""KiminaProver: a whole-proof generation prover (Moonshot AI's Kimina-Prover).

Kimina-Prover is an RL-trained, reasoning-driven model that emits a **complete Lean 4
proof** from a theorem statement -- no external tree search. That maps almost directly
onto our contract: for each ``sorry``'d target we prompt the model, splice the
returned proof body over the ``sorry``, and let the shared :class:`Verifier` be the
authoritative judge. Structurally this is the Aristotle path (generate -> splice ->
verify), except the "model" is one **we serve ourselves on GPU compute via vLLM**
rather than a hosted API.

Generation is isolated behind :meth:`KiminaProver._generate` (statements in,
candidate proof bodies out) so the splice/select/guard logic is fully testable
offline with canned candidates -- the same seam shape as Aristotle's
``_submit_and_download``. The real GPU path runs a one-shot ``kimina_generate.py`` in
the generation backend (Phase B); without a generation backend wired, ``_generate``
raises.

Selection cashes in pass@k honestly: we generate K candidates per target and keep the
**first that compiles, is ``sorry``-free, and leaves the signature intact** -- our own
compile is the source of truth, never the model's first guess.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from open_afps.backends.base import ComputeBackend
from open_afps.core.prover import AutomatedProver, AutomatedProverConfig
from open_afps.core.result import GenerationOutput
from open_afps.core.task import LeanProject, ProofTask
from open_afps.provers._lean_splice import Theorem, extract_theorems, splice_proof
from open_afps.provers.numina_tracker import StatementTracker

# Directories never worth copying into the workdir (mirrors the other provers).
_IGNORE = shutil.ignore_patterns(".lake", ".git", "*.tar.gz")

_SORRY_RE_TOKEN = "sorry"

#: Files exchanged with the one-shot generation entrypoint inside the sandbox.
_STATEMENTS_FILE = "_kimina_statements.jsonl"
_CANDIDATES_FILE = "_kimina_candidates.jsonl"


@dataclass
class KiminaProverConfig(AutomatedProverConfig):
    #: HF model id or a path mounted into the generation image.
    model: str = "AI-MO/Kimina-Prover-Preview-Distill-7B"
    #: Candidates generated per target; quality scales hard with K (pass@k).
    pass_k: int = 32
    temperature: float = 0.6
    max_tokens: int = 8192
    #: GPU the generation backend requests (Modal takes ``"A100"``, ``"H100"``, ...).
    gpu: str = "A100"
    #: Guard against a spliced candidate altering a target's signature.
    guard_statements: bool = True
    extra_env: dict[str, str] = field(default_factory=dict)


class KiminaProver(AutomatedProver):
    name = "kimina"

    config: KiminaProverConfig

    def __init__(
        self,
        config: KiminaProverConfig,
        verification_backend: ComputeBackend,
        generation_backend: ComputeBackend | None = None,
    ) -> None:
        super().__init__(config, verification_backend)
        # The (GPU) backend that serves the model. Optional so tests can stub
        # ``_generate`` and run the splice/select/guard logic with no GPU.
        self.generation_backend = generation_backend

    def prove(self, task: ProofTask, workdir: Path) -> GenerationOutput:
        # 1. Stage the project so the workdir is a complete project to edit in place.
        shutil.copytree(task.project.root, workdir, dirs_exist_ok=True, ignore=_IGNORE)

        # 2. Snapshot original .lean contents for the post-run diff.
        original = {
            p.relative_to(workdir).as_posix(): p.read_text()
            for p in workdir.rglob("*.lean")
            if ".lake" not in p.parts
        }

        # 3. Extract targets: each sorry'd theorem -> (file, Theorem). A name may
        #    repeat across files, so key selection state by (file, name).
        targets = self._extract_targets(task, workdir)
        statements = {th.name: th.statement for _, th in targets}

        # 4. Generate K candidate proof bodies per target name.
        candidates = self._generate(statements, workdir) if statements else {}

        # 5. Statement-change guard: snapshot target files before any splice.
        tracked = sorted({workdir / f for f, _ in targets})
        tracker = (
            StatementTracker(tracked)
            if self.config.guard_statements and tracked
            else None
        )

        # 6. Select by verifying: keep the first candidate per target that compiles
        #    sorry-free and leaves the signature intact.
        winners, samples_tried = self._select(workdir, targets, candidates, tracker)

        # 7. Diff the workdir's .lean files against the staged originals.
        completed: dict[str, str] = {}
        for path in sorted(workdir.rglob("*.lean")):
            if ".lake" in path.parts:
                continue
            rel = path.relative_to(workdir).as_posix()
            content = path.read_text()
            if original.get(rel) != content:
                completed[rel] = content

        return GenerationOutput(
            completed_files=completed,
            # Self-served on our own GPU: there is no per-run dollar cost to report.
            cost_usd=None,
            metadata={
                "model": self.config.model,
                "pass_k": self.config.pass_k,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
                "gpu": self.config.gpu,
                "targets": [f"{f}:{th.name}" for f, th in targets],
                "samples_tried": samples_tried,
                "winning_index": winners,
                "guard_statements": self.config.guard_statements,
            },
        )

    # -- target extraction ----------------------------------------------------

    def _extract_targets(
        self, task: ProofTask, workdir: Path
    ) -> list[tuple[str, Theorem]]:
        """Resolve ``(relative_file, Theorem)`` for every sorry'd target theorem.

        Honours ``task.targets`` when set; otherwise every workdir file carrying a
        ``sorry`` is fair game (mirroring :meth:`ProofTask.resolved_targets`).
        """
        if task.targets:
            files = [workdir / t for t in task.targets]
        else:
            files = [
                p
                for p in sorted(workdir.rglob("*.lean"))
                if ".lake" not in p.parts and _SORRY_RE_TOKEN in p.read_text()
            ]
        out: list[tuple[str, Theorem]] = []
        for f in files:
            if not f.is_file():
                continue
            rel = f.relative_to(workdir).as_posix()
            for th in extract_theorems(f.read_text()):
                out.append((rel, th))
        return out

    # -- selection ------------------------------------------------------------

    def _select(
        self,
        workdir: Path,
        targets: list[tuple[str, Theorem]],
        candidates: dict[str, list[str]],
        tracker: StatementTracker | None,
    ) -> tuple[dict[str, int | None], int]:
        """Splice candidates greedily, keeping the first that holds up per target.

        Works on the live workdir files. The spans in ``targets`` index the *original*
        text, so each candidate is re-located against the current file contents before
        splicing -- cumulative edits from earlier targets stay consistent. Returns
        ``({"file:name": winning_index_or_None}, total_samples_tried)``.

        A candidate wins for its target iff, after splicing, the file compiles, the
        spliced body introduces no ``sorry``, and the statement guard sees no signature
        drift. The final, authoritative whole-project check happens later in
        :meth:`AutomatedProver.run`.
        """
        winners: dict[str, int | None] = {}
        samples_tried = 0
        for rel, th in targets:
            key = f"{rel}:{th.name}"
            winners[key] = None
            for idx, body in enumerate(candidates.get(th.name, [])):
                samples_tried += 1
                if _SORRY_RE_TOKEN in body:
                    continue  # a body that still defers is never a winner
                if self._try_candidate(workdir, rel, th.name, body, tracker):
                    winners[key] = idx
                    break
        return winners, samples_tried

    def _try_candidate(
        self,
        workdir: Path,
        rel: str,
        name: str,
        body: str,
        tracker: StatementTracker | None,
    ) -> bool:
        """Splice ``body`` into target ``name`` of file ``rel`` and judge it.

        Re-resolves the target's span against the current file contents so cumulative
        edits from earlier targets stay consistent. Reverts the file on rejection.
        """
        path = workdir / rel
        before = path.read_text()
        th = self._locate(before, name)
        if th is None:
            return False

        path.write_text(splice_proof(before, th.body_span, body))

        report = self.verifier.verify(LeanProject(workdir))
        compiled = report.per_file.get(rel, False)
        guard_ok = True
        if tracker is not None:
            ok, _ = tracker.check_initial_statements()
            guard_ok = ok

        if compiled and guard_ok:
            return True

        path.write_text(before)  # revert
        return False

    # -- generation seam ------------------------------------------------------

    def _generate(
        self, statements: dict[str, str], workdir: Path
    ) -> dict[str, list[str]]:
        """Generate ``pass_k`` candidate proof bodies per statement on GPU compute.

        Test seam: stub this to return canned candidates and exercise the
        splice/select/guard path with no GPU/model/network (mirrors Aristotle's
        ``_submit_and_download``).

        The real path writes the statements as jsonl into ``workdir``, runs the
        one-shot ``kimina_generate.py`` entrypoint in the generation backend (which
        loads the model once via vLLM and writes a candidates jsonl), and reads the
        results back. Requires a GPU generation backend; CPU Docker cannot serve the
        model.
        """
        if self.generation_backend is None:
            raise RuntimeError(
                "kimina requires a GPU generation backend to serve the model; "
                "none was configured. Pass a Modal GPU backend (see "
                "`open-afps build-kimina-image`), or stub `_generate` in tests."
            )

        (workdir / _STATEMENTS_FILE).write_text(
            "\n".join(
                json.dumps({"name": n, "statement": s}) for n, s in statements.items()
            )
            + "\n"
        )

        command = (
            "python3 /opt/kimina/kimina_generate.py"
            f" --statements {_STATEMENTS_FILE}"
            f" --out {_CANDIDATES_FILE}"
            f" --model {self.config.model}"
            f" --pass-k {self.config.pass_k}"
            f" --temperature {self.config.temperature}"
            f" --max-tokens {self.config.max_tokens}"
        )
        self.generation_backend.run(
            workdir, command, env=self.config.extra_env, timeout_s=self.config.timeout_s
        )

        out_path = workdir / _CANDIDATES_FILE
        if not out_path.is_file():
            raise RuntimeError(
                f"kimina generation produced no {_CANDIDATES_FILE}; "
                "check the generation backend logs."
            )
        candidates: dict[str, list[str]] = {}
        for line in out_path.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            candidates[row["name"]] = list(row.get("candidates", []))
        return candidates

    # -- helpers --------------------------------------------------------------

    @staticmethod
    def _locate(lean_text: str, name: str) -> Theorem | None:
        """Re-find target ``name`` in current ``lean_text`` (spans shift on edits)."""
        for th in extract_theorems(lean_text):
            if th.name == name:
                return th
        return None
