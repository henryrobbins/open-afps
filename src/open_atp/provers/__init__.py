"""Concrete provers and the registry/factory over them."""

from open_atp.provers.agent_prover import AgentProver
from open_atp.provers.aristotle import AristotleProver
from open_atp.provers.base import AutomatedProver, ProofResult
from open_atp.provers.numina import NuminaProver
from open_atp.provers.registry import PROVER_TYPES, available_provers, get_prover

__all__ = [
    "AutomatedProver",
    "AgentProver",
    "AristotleProver",
    "NuminaProver",
    "ProofResult",
    "PROVER_TYPES",
    "available_provers",
    "get_prover",
]
