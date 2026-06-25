"""The prover registry: a type name -> a constructed :class:`AutomatedProver`.

The package is a library: a caller picks a prover, constructs it against a compute
backend, and calls :meth:`~open_atp.provers.base.AutomatedProver.prove` directly::

    from open_atp.provers import get_prover
    from open_atp.backends.docker import DockerBackend

    prover = get_prover("claude", backend=DockerBackend())
    result = prover.prove(task, output_dir)

This module is the registry/factory over that flow:

* :data:`PROVER_TYPES` -- prover *type* name (``agent`` / ``numina`` / ``aristotle``)
  -> the :class:`~open_atp.provers.base.AutomatedProver` subclass. The factory in
  :mod:`open_atp.config` dispatches a ``prover`` spec's ``type`` through this.
* :func:`available_provers` -- every name :func:`get_prover` accepts.
* :func:`get_prover` -- construct a default prover by name against a backend.

Every agentic prover is the shared :class:`~open_atp.provers.agent_prover.AgentProver`;
the harness it carries selects the CLI. :data:`_HARNESS_ALIASES` lets a caller name a
prover by harness (``"codex"`` -> ``AgentProver`` on the Codex harness) without building
the harness by hand.
"""

from __future__ import annotations

from open_atp.backends.base import ComputeBackend
from open_atp.harness import HARNESSES
from open_atp.provers.agent_prover import AgentProver
from open_atp.provers.aristotle import AristotleProver
from open_atp.provers.base import AutomatedProver
from open_atp.provers.numina import NuminaProver

#: Prover *type* name -> the :class:`~open_atp.provers.base.AutomatedProver` subclass.
PROVER_TYPES: dict[str, type[AutomatedProver]] = {
    "agent": AgentProver,
    "numina": NuminaProver,
    "aristotle": AristotleProver,
}

#: Convenience aliases: a non-default harness name -> the default :class:`AgentProver`
#: on that harness. The bare ``"agent"`` type already gives the ``claude_code``
#: default, so it is not duplicated here. Codex authenticates via ChatGPT/OpenAI so its
#: harness defaults to an OpenAI model; ax-prover and vibe carry their own
#: harness-appropriate defaults.
_HARNESS_ALIASES: dict[str, str] = {
    "codex": "codex",
    "opencode": "opencode",
    "axprover": "axprover",
    "vibe": "vibe",
}


def available_provers() -> list[str]:
    """The names :func:`get_prover` accepts: prover types plus harness aliases."""
    return [*PROVER_TYPES, *_HARNESS_ALIASES]


def get_prover(name: str, *, backend: ComputeBackend) -> AutomatedProver:
    """Construct the *default* prover ``name`` against ``backend``.

    ``name`` is either a :data:`PROVER_TYPES` key (``"agent"`` -- the ``claude_code``
    default, ``"numina"``, ``"aristotle"``) or a :data:`_HARNESS_ALIASES` key
    (``"codex"``, ``"opencode"``, ``"axprover"``, ``"vibe"``) selecting an
    :class:`~open_atp.provers.agent_prover.AgentProver` on that harness. The prover is
    built with its class's baked-in defaults; to customize any knob (model, effort,
    max_rounds, ...), construct the prover directly or use
    :func:`open_atp.config.build_prover` with a config dict.

    The sandbox image (and the toolchain + Mathlib pins projects are checked against)
    comes from ``backend``, not a parameter here.

    Parameters
    ----------
    name : str
        The prover to build. Raises :class:`ValueError` for an unknown name.
    backend : ComputeBackend
        The backend the prover runs generation and the shared
        :class:`~open_atp.verify.Verifier` on.

    Returns
    -------
    prover : AutomatedProver
        The constructed default prover, ready to drive via
        :meth:`~open_atp.provers.base.AutomatedProver.prove`.

    Examples
    --------

    Construction is cheap and offline (the backend is wired in, not called):

    >>> from open_atp.backends.docker import DockerBackend
    >>> prover = get_prover("agent", backend=DockerBackend())
    >>> prover.harness.model
    'claude-opus-4-8'
    """
    if name in PROVER_TYPES:
        return PROVER_TYPES[name](backend=backend)
    if name in _HARNESS_ALIASES:
        return AgentProver(harness=HARNESSES[_HARNESS_ALIASES[name]](), backend=backend)
    raise ValueError(f"unknown prover {name!r}; choose from {available_provers()}")
