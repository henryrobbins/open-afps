"""Build provers (with their compute backend and harness) from plain config dicts.

The library's runtime objects -- :class:`~open_atp.provers.base.AutomatedProver`,
:class:`~open_atp.harness.Harness`, :class:`~open_atp.backends.base.ComputeBackend` --
take plain keyword arguments. This module is the thin factory that turns a nested
config dict (e.g. parsed from YAML; parsing is the caller's job, so there is no YAML
dependency here) into a constructed prover::

    from open_atp.config import build_prover

    prover = build_prover({
        "compute": {"type": "modal", "cpu": 2, "memory_mib": 4096},
        "prover": {
            "type": "agent",
            "harness": {"type": "claude_code", "model": "claude-opus-4-8"},
            "skills": ["lean-proof"],
        },
    })

Each level is dispatched on a ``type`` key through its registry
(:data:`~open_atp.backends.BACKENDS`, :data:`~open_atp.harness.HARNESSES`,
:data:`~open_atp.provers.PROVER_TYPES`); the remaining keys become constructor
kwargs. Unknown keys raise -- a typo'd option fails loudly rather than being silently
ignored.
"""

from __future__ import annotations

import inspect
from collections.abc import Mapping
from typing import cast

from open_atp.backends import BACKENDS
from open_atp.backends.base import ComputeBackend
from open_atp.harness import HARNESSES, Harness
from open_atp.provers import PROVER_TYPES
from open_atp.provers.base import AutomatedProver


def _split[T](
    registry: Mapping[str, type[T]], spec: Mapping[str, object], kind: str
) -> tuple[type[T], dict[str, object]]:
    """Resolve ``spec["type"]`` to a class and return ``(cls, kwargs)``.

    ``kwargs`` is ``spec`` minus ``type``; any key that is not a constructor parameter
    of ``cls`` raises :class:`ValueError` (a loud signal for a typo'd option).
    """
    rest = dict(spec)
    type_ = rest.pop("type", None)
    if not isinstance(type_, str) or type_ not in registry:
        raise ValueError(
            f"unknown {kind} type {type_!r}; choose from {sorted(registry)}"
        )
    cls = registry[type_]
    known = set(inspect.signature(cls).parameters) - {"self"}
    extra = set(rest) - known
    if extra:
        raise ValueError(
            f"unknown {type_!r} {kind} option(s) {sorted(extra)}; "
            f"valid: {sorted(known)}"
        )
    return cls, rest


def build_backend(spec: Mapping[str, object]) -> ComputeBackend:
    """Construct a :class:`~open_atp.backends.base.ComputeBackend` from a compute spec.

    ``spec`` is a mapping with a ``type`` (``"docker"`` / ``"modal"``) plus that
    backend's kwargs (e.g. ``{"type": "modal", "cpu": 2}``). A nested ``image`` mapping
    is coerced to an :class:`~open_atp.images.Image` by the backend itself.
    """
    cls, kwargs = _split(BACKENDS, spec, "compute")
    return cls(**kwargs)  # type: ignore[arg-type]  # validated dict -> kwargs


def build_harness(spec: Mapping[str, object] | str) -> Harness:
    """Construct a :class:`~open_atp.harness.Harness` from a harness spec.

    ``spec`` is either a bare type name (``"claude_code"``) or a mapping with a ``type``
    plus the harness's kwargs (``{"type": "vibe", "max_turns": 8}``).
    """
    spec = {"type": spec} if isinstance(spec, str) else spec
    cls, kwargs = _split(HARNESSES, spec, "harness")
    return cls(**kwargs)  # type: ignore[arg-type]  # validated dict -> kwargs


def build_prover(config: Mapping[str, object]) -> AutomatedProver:
    """Construct a fully-wired prover from a ``{compute, prover}`` config dict.

    Builds the backend from ``config["compute"]``, then the prover from
    ``config["prover"]`` (dispatched on its ``type``), recursively building a nested
    ``harness`` spec along the way, and wires the backend in.
    """
    backend = build_backend(cast("Mapping[str, object]", config["compute"]))
    cls, kwargs = _split(
        PROVER_TYPES, cast("Mapping[str, object]", config["prover"]), "prover"
    )
    if "harness" in kwargs:
        kwargs["harness"] = build_harness(
            cast("Mapping[str, object] | str", kwargs["harness"])
        )
    return cls(backend=backend, **kwargs)  # type: ignore[arg-type]  # validated kwargs
