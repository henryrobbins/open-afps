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

Ported from milp_flare's ``harness/`` package. The skills to mount are owned by
the prover (``AgentProver.skills``, resolved to source dirs and handed to
:meth:`Harness.stage_skills`); plugins are Claude-only and live on
``ClaudeCodeHarness.plugins``.
"""

from __future__ import annotations

import shutil
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar

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

    #: Workdir-relative directory this harness mounts skills into (e.g.
    #: ``.claude/skills``), or ``None`` if the harness doesn't consume skills
    #: (ax-prover ships its own). Read by :meth:`stage_skills` and the prover.
    skills_dest: ClassVar[str | None] = None

    def __init__(self, *, model: str = "claude-opus-4-8", effort: str = "high") -> None:
        #: Model id this harness runs.
        self.model = model
        #: Reasoning-effort level passed to harnesses that support it.
        self.effort = effort

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
        """Populate ``wd`` with the harness's launch script.

        Everything the harness itself owns -- *not* the skills list (the prover stages
        it via :meth:`stage_skills`) and *not* the prompt (the prover and task own it,
        written via :meth:`write_prompt`). Subclasses that need more (Vibe's
        VIBE_HOME, ax-prover's per-target setup) override and call ``super().stage``.
        """
        if not wd.exists():
            raise RuntimeError("The agent working directory must be created first.")
        (wd / SCRIPT_FILE).write_text(self._agent_command())

    def write_prompt(self, wd: Path, prompt: str) -> None:
        """Write the composed prompt where this harness's launch script reads it.

        The prompt's *content* is owned by the prover (its prover prompt) and the task
        (the optional user prompt); the harness owns only the file location and the
        ``cat $PROMPT`` launch contract, so it provides the write mechanism.
        """
        (wd / PROMPT_FILE).write_text(prompt)

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

    def stage_skills(self, wd: Path, skill_dirs: list[Path]) -> None:
        """Copy resolved skill source dirs into this harness's skill location.

        Each ``<name>/SKILL.md`` tree lands at ``wd/<skills_dest>/<dir-name>/`` (an
        upstream ``tests/`` fixture dir is dropped). A no-op for a harness that does
        not consume skills (``skills_dest is None``, e.g. ax-prover). The prover owns
        the *list* (``AgentProver.skills``, resolved by ``resolve_skill``);
        the harness owns *where* it goes.
        """
        if self.skills_dest is None or not skill_dirs:
            return
        target = wd / self.skills_dest
        target.mkdir(parents=True, exist_ok=True)
        for skill in skill_dirs:
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


def _infer_provider(model: str) -> str:
    if model.startswith("claude"):
        return "anthropic"
    if model.startswith("deepseek"):
        return "deepseek"
    if model.startswith("gemini"):
        return "google"
    return "openai"
