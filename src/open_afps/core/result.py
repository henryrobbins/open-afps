"""Output types: verification reports and the per-prover proof result."""

from __future__ import annotations

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
    metadata: dict[str, object] = field(default_factory=dict)
    # Set when ``prove()`` already verified the candidate in its own (live) sandbox --
    # the agent/verify backend-reuse path. ``run()`` then skips the standalone verify
    # rather than spinning a second sandbox. ``None`` means "not yet verified".
    verification: VerificationReport | None = None


@dataclass
class ProofResult:
    """What a prover returns for one :class:`~open_afps.core.task.ProofTask`."""

    prover: str
    verification: VerificationReport | None
    completed_files: dict[str, str] = field(default_factory=dict)
    cost_usd: float | None = None
    duration_s: float | None = None
    logs: str = ""
    artifacts_dir: Path | None = None
    metadata: dict[str, object] = field(default_factory=dict)
    # Set when the prover raised before producing a result (Docker down, API error,
    # toolchain mismatch). ``verification`` is ``None`` and ``success`` is ``False``.
    error: str | None = None

    @property
    def success(self) -> bool:
        return bool(self.verification and self.verification.verified)

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
            "metadata": dict(self.metadata),
        }


def _truncate(text: str, limit: int) -> str:
    """Keep the tail of ``text`` (where a run's outcome lives) under ``limit`` chars."""
    if limit <= 0 or len(text) <= limit:
        return text
    omitted = len(text) - limit
    return f"...[{omitted} chars truncated]...\n{text[-limit:]}"
