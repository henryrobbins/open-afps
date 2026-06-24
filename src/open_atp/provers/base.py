"""Base prover abstraction.

An :class:`AutomatedProver` is a *candidate generator*: it takes a
:class:`~open_atp.lean.ProofTask` and a caller-chosen output directory, fills
the project's ``sorry``\\s, verifies the result in a shared sandbox, and returns a
:class:`~open_atp.verify.ProofResult`. The base class owns the shared lifecycle
-- stage the output layout, generate, then verify -- so subclasses only implement
``_generate`` and every prover (including Aristotle) gets the same final check for
free. Concrete provers live alongside this base in ``open_atp.provers``.

The public entry point is :meth:`AutomatedProver.prove`. A caller constructs a prover
directly (or via :func:`open_atp.provers.get_prover`) and calls it::

    result = prover.prove(task, output_dir)

``prove`` populates ``output_dir/{wd,logs}/``: ``wd`` is the completed lake project
and ``logs`` is the run record.
"""

from __future__ import annotations

import abc
import json
import time
from collections.abc import Mapping
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any, Self

from open_atp.backends.base import ComputeBackend
from open_atp.lean import LeanProject, ProofTask
from open_atp.verify import ProofResult, Verifier


@dataclass
class AutomatedProverConfig:
    """Base configuration shared by all provers.

    Subclasses extend with their own knobs:

    * :class:`~open_atp.provers.agent_prover.AgentProverConfig`: harness
      (claude/opencode/codex), effort, skills, MCP.
    * :class:`~open_atp.provers.numina.NuminaProverConfig`: extends the agent config
      + max_rounds, helper API keys.
    * :class:`~open_atp.provers.aristotle.AristotleProverConfig`: api key, mode,
      poll interval.

    The sandbox image (its tag plus the Lean toolchain + Mathlib pins the shared
    verifier checks every project against) lives on the backend's
    :class:`~open_atp.backends.base.BackendConfig`, not here -- a prover inherits
    whatever image its verification backend runs.

    Attributes
    ----------
    timeout_s : int
        Wall-clock budget for the generation run, in seconds. Default ``1800``.
    env : dict[str, str]
        Extra environment variables exported into the run. Default empty.
    """

    timeout_s: int = 1800
    env: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> Self:
        """Build a config from a mapping (e.g. parsed JSON), ignoring unknown keys.

        The inverse of :func:`dataclasses.asdict`: any tuple-typed field is
        restored from the list JSON round-trips it to. Unknown keys are dropped
        so a serialized superset (or a sibling subclass's extra knobs) loads
        cleanly. Non-init fields (e.g. a per-harness config's pinned ``harness``)
        are skipped -- they are fixed by the class, not loaded. Subclasses inherit
        this unchanged -- ``cls`` resolves to the concrete config, so its own
        fields are honoured.
        """
        known = {f.name: f for f in fields(cls) if f.init}
        kwargs: dict[str, Any] = {}
        for key, value in data.items():
            f = known.get(key)
            if f is None:
                continue
            if (
                isinstance(value, list)
                and isinstance(f.type, str)
                and f.type.startswith("tuple")
            ):
                value = tuple(tuple(v) if isinstance(v, list) else v for v in value)
            kwargs[key] = value
        return cls(**kwargs)


class AutomatedProver(abc.ABC):
    """Generate candidate proofs, then verify them in a shared sandbox."""

    name: str = "base"

    def __init__(
        self, config: AutomatedProverConfig, verification_backend: ComputeBackend
    ) -> None:
        self.config = config
        # The backend used for the *final check*. Its image carries the toolchain +
        # Mathlib pins the verifier rejects mismatched projects against. Agentic
        # provers additionally run their generation in a backend; that is the
        # subclass's concern.
        self.verifier = Verifier(verification_backend)

    @abc.abstractmethod
    def _generate(
        self, task: ProofTask, wd: Path, logs_dir: Path, result: ProofResult
    ) -> None:
        """Generate the completed project in ``wd`` and record the run in ``result``.

        Implementations must leave ``wd`` containing the full completed project so the
        verifier can compile it in place, write the run's logs into ``logs_dir``, and
        fill ``result`` (``completed_files``, ``cost_usd``, ``metadata``). A prover that
        already verified the candidate in its own live sandbox sets
        ``result.verification`` itself; otherwise :meth:`prove` runs the shared check.
        """

    def prove(self, task: ProofTask, output_dir: Path | str) -> ProofResult:
        """Full lifecycle: reject-on-mismatch, generate, verify, write the result.

        ``output_dir`` is caller-chosen and is populated as ``output_dir/{wd,logs}/``:
        ``wd`` is the completed lake project (the proof output) and ``logs`` is the run
        record (the agent ``stdout.txt``/``stderr.txt``, ``result.json``, and any
        harness-specific rich logs).
        """
        self.verifier.check_compatible(task.project)

        output_dir = Path(output_dir)
        wd = output_dir / "wd"
        logs_dir = output_dir / "logs"
        wd.mkdir(parents=True, exist_ok=True)
        logs_dir.mkdir(parents=True, exist_ok=True)

        result = ProofResult(prover=self.name, verification=None, output_dir=output_dir)
        start = time.monotonic()
        self._generate(task, wd, logs_dir, result)
        result.duration_s = time.monotonic() - start

        # A prover that ran generation and the final check in one shared sandbox (the
        # agent/verify backend-reuse path) set ``result.verification`` itself; reuse it
        # rather than spinning a second sandbox. Otherwise verify standalone --
        # Aristotle (no sandbox) and the split-backend case land here.
        if result.verification is None:
            result.verification = self.verifier.verify(LeanProject(wd))

        # A self-describing summary so a downloaded logs dir stands on its own.
        (logs_dir / "result.json").write_text(
            json.dumps(result.to_dict(), indent=2, default=str)
        )
        return result
