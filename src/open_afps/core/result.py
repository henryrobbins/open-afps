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

    @property
    def success(self) -> bool:
        return bool(self.verification and self.verification.verified)
