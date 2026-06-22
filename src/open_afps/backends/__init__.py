"""Compute backends: the sandbox primitive used for agent execution and verification."""

from open_afps.backends.base import (
    BackendConfig,
    CommandHandle,
    CommandResult,
    ComputeBackend,
)

__all__ = [
    "BackendConfig",
    "CommandHandle",
    "CommandResult",
    "ComputeBackend",
]
