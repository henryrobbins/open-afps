"""AgentProver: a coding agent + lean-lsp-mcp running in a sandbox.

Port target: milp_flare's ``harness/`` package. An ``AgentProver`` composes:

* a **Harness** (claude_code / opencode / codex) -- knows how to render the agent
  launch script, what auth to forward, and how to parse the agent's streamed output
  for token counts / cost; and
* a **ComputeBackend** -- where that script runs, with Lean+Mathlib and lean-lsp-mcp.

The MILP-specific prompts/skills from milp_flare are replaced with a generic
"fill the sorrys in this project" system prompt + skills.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from open_afps.backends.base import ComputeBackend
from open_afps.core.prover import AutomatedProver, AutomatedProverConfig
from open_afps.core.result import GenerationOutput
from open_afps.core.task import ProofTask


@dataclass
class AgentProverConfig(AutomatedProverConfig):
    harness: str = "claude_code"  # one of: claude_code | opencode | codex
    model: str = "claude-opus-4-8"
    effort: str = "high"
    # Vendored skill/prompt/MCP asset bundle to mount into the workdir.
    assets: str = "default"
    extra_env: dict[str, str] = field(default_factory=dict)


class AgentProver(AutomatedProver):
    name = "agent"

    config: AgentProverConfig

    def __init__(
        self,
        config: AgentProverConfig,
        verification_backend: ComputeBackend,
        agent_backend: ComputeBackend | None = None,
    ) -> None:
        super().__init__(config, verification_backend)
        # Generation may run in a different backend than verification (e.g. Modal for
        # the agent, local Docker for the cheap final check) -- but defaults to shared.
        self.agent_backend = agent_backend or verification_backend

    def prove(self, task: ProofTask, workdir: Path) -> GenerationOutput:
        # TODO(phase 3):
        #   1. Stage project into workdir; drop in assets (skills, .mcp.json, agent.sh)
        #      for self.config.harness. Port Harness.configure_wd from milp_flare.
        #   2. self.agent_backend.start(workdir, agent_command, env=auth) and stream.
        #   3. Parse streamed output for token counts -> cost via a ported cost table.
        #   4. Return changed files.
        raise NotImplementedError("AgentProver.prove not yet implemented")
