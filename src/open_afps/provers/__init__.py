"""Concrete provers and the registry/factory over them."""

from open_afps.provers.agent_prover import AgentProver, AgentProverConfig
from open_afps.provers.aristotle import AristotleProver, AristotleProverConfig
from open_afps.provers.numina import NuminaProver, NuminaProverConfig
from open_afps.provers.registry import PROVERS, available_provers, get_prover

__all__ = [
    "AgentProver",
    "AgentProverConfig",
    "AristotleProver",
    "AristotleProverConfig",
    "NuminaProver",
    "NuminaProverConfig",
    "PROVERS",
    "available_provers",
    "get_prover",
]
