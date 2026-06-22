"""Concrete provers. Import lazily-friendly: heavy deps live behind install extras."""

from open_afps.provers.agent import AgentProver, AgentProverConfig
from open_afps.provers.aristotle import AristotleProver, AristotleProverConfig
from open_afps.provers.numina import NuminaProver, NuminaProverConfig

__all__ = [
    "AgentProver",
    "AgentProverConfig",
    "AristotleProver",
    "AristotleProverConfig",
    "NuminaProver",
    "NuminaProverConfig",
]
