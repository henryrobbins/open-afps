"""The prover registry: name -> a constructed :class:`AutomatedProver`.

The package is a library: a caller picks a prover, constructs it against a compute
backend, and calls :meth:`~open_atp.provers.base.AutomatedProver.prove` directly::

    from open_atp import PROVERS, get_prover
    from open_atp.backends.docker import DockerBackend, DockerConfig

    backend = DockerBackend(DockerConfig(image=DEFAULT_IMAGE))
    prover = get_prover(PROVERS.CLAUDE, verification_backend=backend)
    result = prover.prove(task, output_dir)

This module is just the registry/factory over that flow:

* :class:`PROVERS` -- the available prover names as an enum.
* :func:`available_provers` -- list them.
* :func:`get_prover` -- construct one by name against a compute backend.

Backends: a prover takes one :class:`~open_atp.backends.base.ComputeBackend`. Agentic
provers run generation in a live session over it and then verify in that same hot
sandbox; Aristotle generates over the network and uses the backend only for the final
check.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from open_atp.backends.base import ComputeBackend
from open_atp.harness import (
    AxProverHarnessConfig,
    ClaudeCodeHarnessConfig,
    CodexHarnessConfig,
    HarnessConfig,
    OpenCodeHarnessConfig,
    VibeHarnessConfig,
)
from open_atp.provers.agent_prover import AgentProver, AgentProverConfig
from open_atp.provers.aristotle import AristotleProver, AristotleProverConfig
from open_atp.provers.base import AutomatedProver, AutomatedProverConfig
from open_atp.provers.numina import NuminaProver, NuminaProverConfig

# --- prover registry / factory ---------------------------------------------


class PROVERS(StrEnum):
    """The provers :func:`get_prover` accepts.

    Each member's value is the registry key. ``agent:<harness>`` members select an
    :class:`~open_atp.provers.agent_prover.AgentProver` harness; :attr:`CLAUDE` is the
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
    """A registry row: the prover + config classes backing a name.

    ``harness_config_cls`` (agent provers only) is the
    :class:`~open_atp.harness.HarnessConfig` subclass composed into the
    :class:`~open_atp.provers.agent_prover.AgentProverConfig` -- it selects the harness
    and its defaults. ``None`` for non-agent provers and for Numina (which pins its own
    harness on its config).
    """

    prover_cls: type[AutomatedProver]
    config_cls: type[AutomatedProverConfig]
    harness_config_cls: type[HarnessConfig] | None = None


#: ``PROVERS -> (ProverClass, ConfigClass, HarnessConfigClass)``. Config-driven so
#: callers never hand-wire classes. Every agentic prover is the shared
#: :class:`AgentProver`; the entry's harness config selects the CLI and bakes its
#: harness-appropriate defaults (codex's OpenAI model, ax-prover's effort, vibe's
#: stand-in agent/Magistral model). The registry hands back exactly that default prover
#: -- callers who want to customize construct the config + prover directly.
_REGISTRY: dict[PROVERS, _Entry] = {
    PROVERS.ARISTOTLE: _Entry(AristotleProver, AristotleProverConfig),
    PROVERS.CLAUDE: _Entry(AgentProver, AgentProverConfig, ClaudeCodeHarnessConfig),
    # codex authenticates via ChatGPT/OpenAI (``codex login``), so its harness config
    # defaults to an OpenAI model -- claude-opus can't be served without an Anthropic
    # ``model_providers`` entry.
    PROVERS.CODEX: _Entry(AgentProver, AgentProverConfig, CodexHarnessConfig),
    PROVERS.OPENCODE: _Entry(AgentProver, AgentProverConfig, OpenCodeHarnessConfig),
    # ax-prover-base runs as an AgentProver on the ``axprover`` harness: its own
    # LangGraph proposer->builder->reviewer loop edits the .lean in place, while
    # AgentProver staging/diff/auth and the shared Verifier do the final
    # compile/sorry/axiom check (we don't trust ax-prover's own reviewer).
    PROVERS.AXPROVER: _Entry(AgentProver, AgentProverConfig, AxProverHarnessConfig),
    PROVERS.NUMINA: _Entry(NuminaProver, NuminaProverConfig),
    # ``vibe`` runs as an AgentProver on the ``vibe`` harness driving Mistral Vibe's
    # Lean agent scaffold (the builtin ``lean`` agent *is* Leanstral; api-hosted, no
    # GPU). The real model ``labs-leanstral-2603`` is Labs-gated (403 until a Mistral
    # org admin enables Labs), so VibeHarnessConfig defaults to Magistral -- a non-Labs
    # *reasoning* model any La Plateforme key can reach -- on the ``lean-standin``
    # profile. To swap the model, construct ``VibeHarnessConfig(model=...)`` directly;
    # vibe has no ``--model`` flag, so the harness templates it into the stand-in
    # profile at launch. Repoint to the Labs model once enabled.
    PROVERS.VIBE: _Entry(AgentProver, AgentProverConfig, VibeHarnessConfig),
}


def available_provers() -> list[PROVERS]:
    """The provers :func:`get_prover` accepts."""
    return list(PROVERS)


def get_prover(
    name: PROVERS | str,
    *,
    verification_backend: ComputeBackend,
) -> AutomatedProver:
    """Construct the *default* prover ``name`` against a compute backend.

    ``name`` is a :class:`PROVERS` member (or its string value). The prover is built
    with its config class's baked-in defaults -- this factory is a shortcut for the
    out-of-the-box provers only. To customize any knob (model, effort, max_rounds, a
    harness-specific guard, ...), construct the config and prover directly instead::

        from open_atp.harness import ClaudeCodeHarnessConfig
        from open_atp.provers import AgentProver, AgentProverConfig

        harness = ClaudeCodeHarnessConfig(model="claude-sonnet-4-6", effort="low")
        prover = AgentProver(AgentProverConfig(harness=harness), backend)

    The sandbox image (and the toolchain + Mathlib pins projects are checked against)
    comes from ``verification_backend``'s config, not a parameter here. Agentic provers
    run their generation in a live session over this same backend and verify in that hot
    sandbox.

    Parameters
    ----------
    name : PROVERS or str
        The prover to build -- a :class:`PROVERS` member or its registry-key string
        (e.g. ``PROVERS.CLAUDE`` or ``"agent"``). Raises :class:`ValueError` for an
        unknown name.
    verification_backend : ComputeBackend
        The backend this prover runs on: the shared :class:`~open_atp.verify.Verifier`'s
        final compile/sorry/axiom check, and -- for agentic provers -- generation in a
        live session over it.

    Returns
    -------
    prover : AutomatedProver
        The constructed default prover, ready to drive via
        :meth:`~open_atp.provers.base.AutomatedProver.prove`.

    Examples
    --------

    Construction is cheap and offline (the backend is wired in, not called), so the
    factory builds a ready-to-drive prover directly from the name's defaults:

    >>> from open_atp import PROVERS, get_prover
    >>> from open_atp.backends.docker import DockerBackend, DockerConfig
    >>> from open_atp.images import DEFAULT_IMAGE
    >>> backend = DockerBackend(DockerConfig(image=DEFAULT_IMAGE))
    >>> prover = get_prover(PROVERS.CLAUDE, verification_backend=backend)
    >>> prover.config.harness.model
    'claude-opus-4-8'

    For a customized prover, construct the config + prover directly -- see each prover
    class for a family-specific example
    (:class:`~open_atp.provers.agent_prover.AgentProver`,
    :class:`~open_atp.provers.numina.NuminaProver`,
    :class:`~open_atp.provers.aristotle.AristotleProver`).

    Drive a constructed prover with
    :meth:`~open_atp.provers.base.AutomatedProver.prove` (this step runs the sandbox,
    so it needs a working Docker backend):

    .. code-block:: python

        from pathlib import Path
        from open_atp.lean import LeanProject, ProofTask

        task = ProofTask(project=LeanProject("path/to/lake/project"))
        result = prover.prove(task, output_dir=Path("runs/demo"))
        result.success      # compiles, sorry-free, no foreign axioms
        result.cost_usd     # estimated USD, when the prover reports it
        result.duration_s   # wall-clock seconds

    See :doc:`/user_guide/run_provers` for more example usage.
    """
    try:
        prover = name if isinstance(name, PROVERS) else PROVERS(name)
    except ValueError:
        raise ValueError(
            f"Unknown prover {name!r}; choose from {[p.value for p in PROVERS]}."
        ) from None
    entry = _REGISTRY[prover]
    # Agent entries compose the name's harness config; the rest use their config's own
    # defaults (Numina pins its harness; Aristotle has none).
    if entry.harness_config_cls is not None:
        config: AutomatedProverConfig = entry.config_cls(
            harness=entry.harness_config_cls()  # type: ignore[call-arg]
        )
    else:
        config = entry.config_cls()

    # Every prover takes (config, backend): agentic provers run generation in a live
    # session over it; Aristotle generates over the network and uses it only to verify.
    return entry.prover_cls(config, verification_backend)
