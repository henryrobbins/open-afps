"""Concrete provers and the registry/factory over them."""

from open_atp.provers.agent_prover import AgentProver, AgentProverConfig
from open_atp.provers.aristotle import AristotleProver, AristotleProverConfig
from open_atp.provers.base import ProofResult
from open_atp.provers.numina import NuminaProver, NuminaProverConfig
from open_atp.provers.registry import PROVERS, available_provers, get_prover

__all__ = [
    "AgentProver",
    "AgentProverConfig",
    "AristotleProver",
    "AristotleProverConfig",
    "NuminaProver",
    "NuminaProverConfig",
    "ProofResult",
    "PROVERS",
    "available_provers",
    "get_prover",
]
