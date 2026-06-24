"""Output types: verification reports and the per-prover proof result."""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

# Axioms that a "clean" Mathlib proof is allowed to depend on. Anything else
# (notably ``sorryAx``) means the proof is not actually complete.
STANDARD_AXIOMS = frozenset({"propext", "Classical.choice", "Quot.sound"})


@dataclass(frozen=True)
class VerificationReport:
    """Result of compiling a candidate project in a sandbox.

    Produced by :class:`~open_afps.core.verifier.Verifier` and shared by every
    prover, including Aristotle.

    Attributes
    ----------
    compiles : bool
        Whether the whole project built successfully.
    sorry_free : bool
        Whether the build is free of ``sorry`` (no incomplete proofs remain).
    axioms : tuple[str, ...]
        Every axiom the compiled project depends on, as reported by Lean.
    compile_log : str
        The full build log. Omitted from :meth:`to_dict`.
    per_file : dict[str, bool]
        Per-file compile status, keyed by file path relative to the project root.
    non_standard_axioms : tuple[str, ...]
        The axioms outside :data:`STANDARD_AXIOMS` -- notably ``sorryAx``, which
        means the proof is not actually complete.
    verified : bool
        True iff the project compiles, has no ``sorry``, and uses no axioms
        outside :data:`STANDARD_AXIOMS`.
    """

    compiles: bool
    sorry_free: bool
    axioms: tuple[str, ...] = ()
    compile_log: str = ""
    per_file: dict[str, bool] = field(default_factory=dict)

    @property
    def non_standard_axioms(self) -> tuple[str, ...]:
        return tuple(a for a in self.axioms if a not in STANDARD_AXIOMS)

    @property
    def verified(self) -> bool:
        """True iff the project compiles, has no sorry, and no foreign axioms."""
        return self.compiles and self.sorry_free and not self.non_standard_axioms

    def to_dict(self) -> dict[str, object]:
        """JSON-ready summary (the full ``compile_log`` is intentionally omitted)."""
        return {
            "verified": self.verified,
            "compiles": self.compiles,
            "sorry_free": self.sorry_free,
            "axioms": list(self.axioms),
            "non_standard_axioms": list(self.non_standard_axioms),
            "per_file": dict(self.per_file),
        }


@dataclass
class GenerationOutput:
    """What a prover's ``prove()`` produces, before the shared verification step.

    ``run()`` merges this with the :class:`VerificationReport` into a
    :class:`ProofResult`. Cost/logs/metadata are optional so a prover can surface
    whatever it knows (agent token cost, Aristotle's run summary, ...).
    """

    completed_files: dict[str, str] = field(default_factory=dict)
    cost_usd: float | None = None
    logs: str = ""
    # The agent's captured stderr (Modal's ``modal_stderr.txt`` / a one-shot run's
    # stderr). Empty when there is no separate error channel (e.g. Aristotle). The
    # base ``run`` writes it to ``logs/stderr.txt``.
    stderr: str = ""
    metadata: dict[str, object] = field(default_factory=dict)
    # Set when ``prove()`` already verified the candidate in its own (live) sandbox --
    # the agent/verify backend-reuse path. ``run()`` then skips the standalone verify
    # rather than spinning a second sandbox. ``None`` means "not yet verified".
    verification: VerificationReport | None = None


@dataclass
class ProofResult:
    """What a prover returns for one :class:`~open_afps.core.task.ProofTask`.

    Attributes
    ----------
    prover : str
        Name of the prover that produced this result.
    verification : VerificationReport or None
        The shared verification of the completed project, or ``None`` when the run
        failed before a candidate could be verified (see :attr:`error`).
    completed_files : dict[str, str]
        The completed ``.lean`` sources, keyed by file path relative to the project
        root.
    cost_usd : float, optional
        Estimated USD cost of the run. ``None`` when the prover does not report cost.
    duration_s : float, optional
        Wall-clock duration of the run, in seconds.
    logs : str
        The run's primary log text. Truncated to the tail by :meth:`to_dict`.
    artifacts_dir : pathlib.Path, optional
        The working directory the run produced -- a complete lake project with the
        completed ``.lean`` files (the proof output). Cloned by :meth:`download_wd`.
    logs_dir : pathlib.Path, optional
        The run's logs directory -- a flat dir holding the captured agent stream
        (``stdout.jsonl``), ``stderr.txt``, and any harness-specific rich record
        (Vibe's session log, ax-prover's per-target logs, Aristotle's events). It sits
        beside ``artifacts_dir`` (``<run>/<label>/{wd,logs}/``) and is the proof
        output's counterpart -- copied out by :meth:`download_logs`.
    metadata : dict[str, object]
        Harness-specific run metadata (token counts, run summaries, ...).
    error : str, optional
        Set when the prover raised before producing a result (Docker down, API error,
        toolchain mismatch). :attr:`verification` is ``None`` and :attr:`success` is
        ``False``.
    success : bool
        True iff :attr:`verification` exists and is
        :attr:`~VerificationReport.verified`.
    """

    prover: str
    verification: VerificationReport | None
    completed_files: dict[str, str] = field(default_factory=dict)
    cost_usd: float | None = None
    duration_s: float | None = None
    logs: str = ""
    artifacts_dir: Path | None = None
    logs_dir: Path | None = None
    metadata: dict[str, object] = field(default_factory=dict)
    error: str | None = None

    @property
    def success(self) -> bool:
        return bool(self.verification and self.verification.verified)

    def download_wd(self, dest: Path | str) -> Path:
        """Clone the completed working directory (the proof project) into ``dest``.

        The package's user picks where run artifacts land; this copies the project
        as it ran -- completed ``.lean`` files plus the harness scaffolding -- but not
        the logs (those go through :meth:`download_logs`). Raises if the run produced
        no workdir (e.g. it failed before generation).
        """
        if self.artifacts_dir is None or not Path(self.artifacts_dir).is_dir():
            raise FileNotFoundError(
                f"{self.prover!r} has no working directory to download"
            )
        dest = Path(dest)
        shutil.copytree(self.artifacts_dir, dest, dirs_exist_ok=True)
        return dest

    def download_logs(self, dest: Path | str) -> Path:
        """Copy the run's logs (agent JSONL, stderr, rich records) into ``dest``.

        The common counterpart to :meth:`download_wd`: every prover funnels its run
        record here regardless of where the CLI originally wrote it. Raises if the run
        produced no logs directory.
        """
        if self.logs_dir is None or not Path(self.logs_dir).is_dir():
            raise FileNotFoundError(f"{self.prover!r} has no logs to download")
        dest = Path(dest)
        shutil.copytree(self.logs_dir, dest, dirs_exist_ok=True)
        return dest

    def to_dict(self, *, log_limit: int = 4000) -> dict[str, object]:
        """JSON-ready view: inline files, verification, cost, and truncated logs."""
        return {
            "prover": self.prover,
            "success": self.success,
            "error": self.error,
            "verification": self.verification.to_dict() if self.verification else None,
            "completed_files": dict(self.completed_files),
            "cost_usd": self.cost_usd,
            "duration_s": self.duration_s,
            "logs": _truncate(self.logs, log_limit),
            "artifacts_dir": str(self.artifacts_dir) if self.artifacts_dir else None,
            "logs_dir": str(self.logs_dir) if self.logs_dir else None,
            "metadata": dict(self.metadata),
        }


def _truncate(text: str, limit: int) -> str:
    """Keep the tail of ``text`` (where a run's outcome lives) under ``limit`` chars."""
    if limit <= 0 or len(text) <= limit:
        return text
    omitted = len(text) - limit
    return f"...[{omitted} chars truncated]...\n{text[-limit:]}"
