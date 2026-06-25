"""Compute backends: the sandbox primitive used for agent execution and verification."""

from open_atp.backends.base import (
    CommandHandle,
    CommandResult,
    ComputeBackend,
)
from open_atp.backends.docker import DockerBackend
from open_atp.backends.modal import ModalBackend

#: Backend registry by name (``ComputeBackend.name`` -> backend class). The factory in
#: :mod:`open_atp.config` dispatches a ``compute`` spec's ``type`` through this.
BACKENDS: dict[str, type[ComputeBackend]] = {
    "docker": DockerBackend,
    "modal": ModalBackend,
}

__all__ = [
    "CommandHandle",
    "CommandResult",
    "ComputeBackend",
    "DockerBackend",
    "ModalBackend",
    "BACKENDS",
]
