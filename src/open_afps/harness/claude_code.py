"""Claude Code CLI harness."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

from open_afps.harness._paths import _MCP_JSON, _SCRIPTS
from open_afps.harness.base import AuthSpec, Harness, HarnessRunResult


class ClaudeCodeHarness(Harness):
    """Claude Code CLI, authenticated by a long-lived ``CLAUDE_CODE_OAUTH_TOKEN``."""

    name = "claude_code"

    def configure_wd(self, wd: Path, prompt: str) -> None:
        super().configure_wd(wd, prompt)
        # Project-scope MCP config (passed via --mcp-config) and skills.
        shutil.copy2(_MCP_JSON, wd / ".mcp.json")
        self._copy_skills(wd, ".claude/skills")

    def static_env(self) -> dict[str, str]:
        # Lets bypassPermissions run non-interactively in the container.
        return {"IS_SANDBOX": "1"}

    def auth_spec(self) -> AuthSpec:
        # A long-lived token (from `claude setup-token`) bills against a Claude
        # subscription rather than at the higher per-API-call rate.
        if "CLAUDE_CODE_OAUTH_TOKEN" not in os.environ:
            raise RuntimeError(
                "claude_code harness requires CLAUDE_CODE_OAUTH_TOKEN"
                " from `claude setup-token`"
            )
        return AuthSpec(env=["CLAUDE_CODE_OAUTH_TOKEN"])

    def _agent_command(self) -> str:
        return self._render((_SCRIPTS / "claude_code_agent.sh").read_text())

    def _parse_lines(self, lines: list[str]) -> HarnessRunResult:
        """Parse ``claude -p --output-format stream-json`` output."""
        result = HarnessRunResult()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("type") == "result":
                result.stop_reason = obj.get("stop_reason")
                result.cost_usd = obj.get("total_cost_usd")
                result.subtype = obj.get("subtype")
                rt = obj.get("result")
                result.result_text = rt if isinstance(rt, str) else None
                usage = obj.get("usage", {})
                result.input_tokens = usage.get("input_tokens", result.input_tokens)
                result.output_tokens = usage.get("output_tokens", result.output_tokens)
        return result
