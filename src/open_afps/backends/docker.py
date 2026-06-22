"""Local Docker backend (skeleton).

Port target: milp_flare ``harness/runner/docker.py``. The mechanics there:

* ``docker run`` with the workdir bind-mounted at a fixed path (``/workspace/wd``).
* A unique container name (``afps-<uuid>``) so a run can be cancelled with
  ``docker kill``.
* Auth/env forwarded via ``-e`` and home dirs (``~/.codex`` etc.) via ``-v``.
* stdout streamed line-by-line; stderr captured to a file.

Phase 1 leaves the subprocess wiring as a TODO and pins down the interface so the
verifier and provers can be built and tested against a fake backend.
"""

from __future__ import annotations

import uuid
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from open_afps.backends.base import BackendConfig, CommandHandle, ComputeBackend


@dataclass
class DockerConfig(BackendConfig):
    # Path inside the container where the workdir is mounted.
    workdir_mount: str = "/workspace/wd"
    # Extra ``-v host:container`` mounts (e.g. agent credential dirs).
    volumes: tuple[tuple[str, str], ...] = ()


class DockerBackend(ComputeBackend):
    config: DockerConfig

    def __init__(self, config: DockerConfig) -> None:
        super().__init__(config)

    @property
    def name(self) -> str:
        return "docker"

    def start(
        self,
        workdir: Path,
        command: str,
        *,
        env: Mapping[str, str] | None = None,
        timeout_s: int | None = None,
    ) -> CommandHandle:
        container = f"afps-{uuid.uuid4().hex[:12]}"
        # TODO(phase 1): build the `docker run --name {container} -v {workdir}:{mount}
        #   -e ... {image} bash -lc {command}` argv, Popen it, and wrap stdout in a
        #   CommandHandle subclass. Port directly from milp_flare/runner/docker.py.
        raise NotImplementedError(
            f"DockerBackend.start not yet ported (would launch container {container})"
        )
