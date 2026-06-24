"""The prover registry: name -> a constructed :class:`AutomatedProver`.

The package is a library: a caller picks a prover, constructs it against a compute
backend, and calls :meth:`~open_afps.provers.base.AutomatedProver.prove` directly::

    from open_afps import PROVERS, get_prover
    from open_afps.backends.docker import DockerBackend, DockerConfig

    backend = DockerBackend(DockerConfig(image=DEFAULT_IMAGE))
    prover = get_prover(PROVERS.CLAUDE, verification_backend=backend)
    result = prover.prove(task, output_dir)

This module is just the registry/factory over that flow:

* :class:`PROVERS` -- the available prover names as an enum.
* :func:`available_provers` -- list them.
* :func:`get_prover` -- construct one by name with a shared image + verify backend.

Backends: the verifier (cheap final check) and the agent (generation) backends are
kept separate -- the split already exists in ``AgentProver`` -- so a job can run
generation on Modal and the check on local Docker.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum

from open_afps.backends.base import ComputeBackend
from open_afps.images import DEFAULT_IMAGE, DEFAULT_TOOLCHAIN
from open_afps.provers.agent_prover import AgentProver, AgentProverConfig
from open_afps.provers.aristotle import AristotleProver, AristotleProverConfig
from open_afps.provers.base import AutomatedProver, AutomatedProverConfig
from open_afps.provers.numina import NuminaProver, NuminaProverConfig

# --- prover registry / factory ---------------------------------------------


class PROVERS(StrEnum):
    """The provers :func:`get_prover` accepts.

    Each member's value is the registry key. ``agent:<harness>`` members select an
    :class:`~open_afps.provers.agent_prover.AgentProver` harness; :attr:`CLAUDE` is the
    bare ``agent`` (config default, ``claude_code``).
    """

    CLAUDE = "agent"
    CODEX = "agent:codex"
    OPENCODE = "agent:opencode"
    AXPROVER = "agent:axprover"
    NUMINA = "numina"
    VIBE = "vibe"
    ARISTOTLE = "aristotle"


@dataclass(frozen=True)
class _Entry:
    """A registry row: which classes back a prover, plus baked-in config."""

    prover_cls: type[AutomatedProver]
    config_cls: type[AutomatedProverConfig]
    # Config overrides implied by the name itself (e.g. ``agent:codex`` -> codex).
    defaults: Mapping[str, object] = field(default_factory=dict)


#: ``PROVERS -> (ProverClass, ConfigClass, defaults)``. Config-driven so callers never
#: hand-wire classes.
_REGISTRY: dict[PROVERS, _Entry] = {
    PROVERS.ARISTOTLE: _Entry(AristotleProver, AristotleProverConfig),
    PROVERS.CLAUDE: _Entry(AgentProver, AgentProverConfig),
    # codex authenticates via ChatGPT/OpenAI (``codex login``), so it must run an
    # OpenAI model -- not the AgentProverConfig default (``claude-opus-4-8``), which
    # codex can't serve without an Anthropic ``model_providers`` entry.
    PROVERS.CODEX: _Entry(
        AgentProver, AgentProverConfig, {"harness": "codex", "model": "gpt-5.5"}
    ),
    PROVERS.OPENCODE: _Entry(AgentProver, AgentProverConfig, {"harness": "opencode"}),
    # ax-prover-base runs as an AgentProver on the ``axprover`` harness: its own
    # LangGraph proposer->builder->reviewer loop edits the .lean in place, while
    # AgentProver staging/diff/auth and the shared Verifier do the final
    # compile/sorry/axiom check (we don't trust ax-prover's own reviewer).
    PROVERS.AXPROVER: _Entry(
        AgentProver,
        AgentProverConfig,
        {"harness": "axprover", "model": "claude-opus-4-8", "effort": "high"},
    ),
    PROVERS.NUMINA: _Entry(NuminaProver, NuminaProverConfig),
    # ``vibe`` runs as an AgentProver on the ``vibe`` harness driving Mistral Vibe's
    # Lean agent scaffold (the builtin ``lean`` agent *is* Leanstral; api-hosted, no
    # GPU). The real model ``labs-leanstral-2603`` is Labs-gated (403 until a Mistral
    # org admin enables Labs), so this defaults to Magistral -- a non-Labs *reasoning*
    # model any La Plateforme key can reach. The model is a knob, like the agent specs:
    # ``overrides={"model": "devstral-medium-latest"}`` swaps it. Vibe has no
    # ``--model`` flag, so the harness templates the model into the vendored
    # ``lean-standin`` profile at launch. Rename/repoint to the Labs model once enabled.
    PROVERS.VIBE: _Entry(
        AgentProver,
        AgentProverConfig,
        {
            "harness": "vibe",
            "agent": "lean-standin",
            "model": "magistral-medium-latest",
        },
    ),
}


def available_provers() -> list[PROVERS]:
    """The provers :func:`get_prover` accepts."""
    return list(PROVERS)


def get_prover(
    name: PROVERS | str,
    *,
    image: str = DEFAULT_IMAGE,
    toolchain: str = DEFAULT_TOOLCHAIN,
    verification_backend: ComputeBackend,
    agent_backend: ComputeBackend | None = None,
    overrides: Mapping[str, object] | None = None,
) -> AutomatedProver:
    """Construct the prover ``name`` with the shared image + verify backend.

    ``name`` is a :class:`PROVERS` member (or its string value). The config is built
    from ``image``/``toolchain`` + the name's baked-in defaults + caller ``overrides``
    (per-prover knobs: model, effort, max_rounds, ...). Agentic provers also receive
    ``agent_backend`` for generation (defaults to the verify backend), keeping the
    agent-vs-verify backend split available.
    """
    try:
        prover = name if isinstance(name, PROVERS) else PROVERS(name)
    except ValueError:
        raise ValueError(
            f"Unknown prover {name!r}; choose from {[p.value for p in PROVERS]}."
        ) from None
    entry = _REGISTRY[prover]

    kwargs: dict[str, object] = {"image": image, "supported_toolchain": toolchain}
    kwargs.update(entry.defaults)
    if overrides:
        kwargs.update(overrides)
    config = entry.config_cls(**kwargs)  # type: ignore[arg-type]

    # Agentic provers take (config, verify_backend, agent_backend); Aristotle does
    # its generation over the network and takes only the verify backend.
    if isinstance(config, AgentProverConfig):
        return entry.prover_cls(config, verification_backend, agent_backend)  # type: ignore[call-arg]
    return entry.prover_cls(config, verification_backend)
