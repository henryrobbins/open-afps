"""The harness contract: the *agent* concern of :class:`~...agent_prover.AgentProver`.

A :class:`Harness` knows, for one agent CLI (Claude Code / Codex / OpenCode):

* how to populate the working directory from its assets (launch script, MCP
  config, skills) -- :meth:`Harness.stage` -- and where to write the prompt the
  prover hands it -- :meth:`Harness.write_prompt`;
* the bash command that launches the agent -- :attr:`Harness.command`;
* which credentials to forward into the sandbox -- :meth:`Harness.auth_spec`; and
* how to read token/cost totals out of the agent's streamed JSON
  -- :meth:`Harness.parse`.

The *compute* concern (where that command runs, with Lean+Mathlib and a warm
cache) lives in the injected :class:`~open_atp.backends.base.ComputeBackend`.

Ported from milp_flare's ``harness/`` package; skills/plugins to mount are
carried by the injected :class:`~open_atp.harness.bundles.AssetBundle` (the
default mounts the vendored ``lean-proof`` skill, plus the ``lean4`` plugin for
the Claude harness).
"""

from __future__ import annotations

import shutil
from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any, ClassVar, Self

from open_atp.harness.bundles import DEFAULT_BUNDLE, AssetBundle

#: Files the harness writes into the workdir; named so they never collide with a
#: project's own sources.
SCRIPT_FILE = "agent.sh"
PROMPT_FILE = "agent_prompt.txt"


@dataclass(frozen=True)
class AuthSpec:
    """Compute-agnostic description of the credentials a harness needs.

    Attributes
    ----------
    env:
        Host environment-variable names to forward into the sandbox.
    home_dirs:
        Host directories to expose under the sandbox's ``$HOME``, as
        ``(host_dir, dest_basename)`` pairs (e.g. ``(~/.codex, ".codex")``).
    """

    env: list[str] = field(default_factory=list)
    home_dirs: list[tuple[Path, str]] = field(default_factory=list)


@dataclass
class HarnessRunResult:
    """Token totals and cost parsed from an agent's streamed output."""

    input_tokens: int = 0
    output_tokens: int = 0
    stop_reason: str | None = None
    #: USD cost if the harness self-reports it (Claude Code, OpenCode); ``None``
    #: when it must be estimated from token counts (Codex).
    cost_usd: float | None = None
    #: Final ``type:"result"`` subtype (Claude Code: ``success`` /
    #: ``error_max_turns`` / ``error_during_execution``). Used by NuminaProver's
    #: round loop to decide continue-vs-stop when no END_REASON marker is present.
    subtype: str | None = None
    #: The agent's final result text (Claude Code's ``result`` field), where the
    #: Numina coordinator prints its ``END_REASON:<reason>`` marker.
    result_text: str | None = None


class Harness(ABC):
    """Base class for an agent CLI harness."""

    name: ClassVar[str]

    def __init__(
        self, config: HarnessConfig, assets: AssetBundle | None = None
    ) -> None:
        self.config = config
        self.assets = assets or DEFAULT_BUNDLE

    @property
    def model(self) -> str:
        """The model id this harness runs (read from its :class:`HarnessConfig`)."""
        return self.config.model

    @property
    def effort(self) -> str:
        """The reasoning-effort level (read from its :class:`HarnessConfig`)."""
        return self.config.effort

    @property
    def command(self) -> str:
        """Bash command the backend runs to launch the agent.

        The backend has already ``cd``'d into the workdir and symlinked ``.lake``;
        we export ``$PROMPT`` from the written prompt file (the launch scripts
        reference it) and run the rendered script.
        """
        return f'export PROMPT="$(cat {PROMPT_FILE})" && bash {SCRIPT_FILE}'

    def static_env(self) -> dict[str, str]:
        """Non-secret env vars to set for this harness (e.g. ``IS_SANDBOX``)."""
        return {}

    def auth_spec(self) -> AuthSpec:
        """Credentials to forward into the sandbox for this harness."""
        return AuthSpec()

    def stage(self, wd: Path) -> None:
        """Populate ``wd`` with the launch script, MCP config, skills, and extra dirs.

        Everything the harness and its asset bundle own -- *not* the prompt, which the
        prover and task own and write via :meth:`write_prompt`.
        """
        if not wd.exists():
            raise RuntimeError("The agent working directory must be created first.")
        (wd / SCRIPT_FILE).write_text(self._agent_command())
        self._copy_extra_dirs(wd)

    def write_prompt(self, wd: Path, prompt: str) -> None:
        """Write the composed prompt where this harness's launch script reads it.

        The prompt's *content* is owned by the prover (its prover prompt) and the task
        (the optional user prompt); the harness owns only the file location and the
        ``cat $PROMPT`` launch contract, so it provides the write mechanism.
        """
        (wd / PROMPT_FILE).write_text(prompt)

    def _copy_extra_dirs(self, wd: Path) -> None:
        """Copy the bundle's extra asset trees (e.g. Numina's prompts) into ``wd``."""
        for src, dest in self.assets.extra_dirs:
            target = wd / dest
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(src, target, dirs_exist_ok=True)

    def parse(self, lines: list[str]) -> HarnessRunResult:
        """Parse the agent's streamed JSON lines into a :class:`HarnessRunResult`."""
        return self._parse_lines(lines)

    def collect_logs(self, wd: Path, logs_dir: Path) -> None:
        """Move this harness's rich log files out of ``wd`` into ``logs_dir``.

        The streamed event JSONL the prover captures from stdout *is* the agent's
        transcript for every CLI harness, so the default does nothing. Harnesses that
        *also* drop a richer record inside the workdir (Vibe's session log, ax-prover's
        per-target logs) override this to relocate those files -- so ``download_wd``
        stays the proof project and ``download_logs`` carries the full record. Called
        after :meth:`parse` (which may read those files for cost), so moving them is
        safe.
        """

    def _copy_skills(self, wd: Path, dest: str) -> None:
        """Copy the selected bundle's skills into ``wd/<dest>``.

        Two mount modes (a bundle may use either or both):

        * each dir in ``skills`` -> ``wd/<dest>/<dir-name>/`` (ordinary named
          skills; an upstream ``tests/`` fixture dir is dropped); and
        * the legacy ``skills_dir`` -> its *contents* to ``wd/<dest>/`` (a single
          root-mounted skill bundle, e.g. Numina).

        A no-op when the bundle mounts no skills.
        """
        if self.assets.skills_dir is None and not self.assets.skills:
            return
        target = wd / dest
        target.mkdir(parents=True, exist_ok=True)
        if self.assets.skills_dir is not None:
            shutil.copytree(self.assets.skills_dir, target, dirs_exist_ok=True)
        for skill in self.assets.skills:
            shutil.copytree(
                skill,
                target / skill.name,
                ignore=shutil.ignore_patterns("tests"),
                dirs_exist_ok=True,
            )

    def _render(self, template: str) -> str:
        """Substitute ``<<MODEL>>``/``<<EFFORT>>`` into a launch-script template."""
        return template.replace("<<MODEL>>", self.model).replace(
            "<<EFFORT>>", self.effort
        )

    @abstractmethod
    def _agent_command(self) -> str:
        """The rendered contents of the workdir's ``agent.sh``."""

    @abstractmethod
    def _parse_lines(self, lines: list[str]) -> HarnessRunResult: ...


@dataclass
class HarnessConfig:
    """Declarative, serializable config for one agent CLI harness.

    Mirrors the :class:`~open_atp.backends.base.BackendConfig` ->
    :class:`~open_atp.backends.base.ComputeBackend` split: this config is the spec
    (the knob set), and :meth:`build` constructs the runtime :class:`Harness` from
    it. Each harness ships a subclass next to it that sets :attr:`harness_cls` and
    adds the knobs that harness honours (e.g.
    :class:`~open_atp.harness.vibe.VibeHarnessConfig`'s ``agent``/``max_turns``/
    ``max_price``). ``model`` and ``effort`` are shared by every harness and live
    here on the base.

    Attributes
    ----------
    model : str
        Model id the harness runs. Default ``claude-opus-4-8``.
    effort : str
        Reasoning-effort level passed to harnesses that support it. Default
        ``high``.
    """

    model: str = "claude-opus-4-8"
    effort: str = "high"

    #: The harness class :meth:`build` instantiates; set by each subclass.
    harness_cls: ClassVar[type[Harness]]

    def build(self, assets: AssetBundle | None = None) -> Harness:
        """Construct the harness this config describes, from a resolved asset bundle."""
        return self.harness_cls(self, assets)

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> Self:
        """Build from a mapping (e.g. parsed JSON), ignoring unknown keys."""
        known = {f.name for f in fields(cls) if f.init}
        kwargs: dict[str, Any] = {k: v for k, v in data.items() if k in known}
        return cls(**kwargs)


def _infer_provider(model: str) -> str:
    if model.startswith("claude"):
        return "anthropic"
    if model.startswith("deepseek"):
        return "deepseek"
    if model.startswith("gemini"):
        return "google"
    return "openai"
