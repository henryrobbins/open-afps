"""Codex CLI harness."""

from __future__ import annotations

import json
from pathlib import Path

from open_afps.harness._paths import _SCRIPTS
from open_afps.harness.base import AuthSpec, Harness, HarnessRunResult


class CodexHarness(Harness):
    """Codex CLI, authenticated by a bind-mounted ``~/.codex`` credential dir."""

    name = "codex"

    def configure_wd(self, wd: Path, prompt: str) -> None:
        super().configure_wd(wd, prompt)
        # Codex registers the MCP server via -c overrides in the launch script;
        # only the skills need copying. https://developers.openai.com/codex/skills
        self._copy_skills(wd, ".agents/skills")

    def auth_spec(self) -> AuthSpec:
        # Mounted rw because codex refreshes its access token mid-session.
        codex_dir = Path.home() / ".codex"
        if not codex_dir.exists():
            raise RuntimeError("codex harness requires ~/.codex from `codex login`")
        return AuthSpec(home_dirs=[(codex_dir, ".codex")])

    def _agent_command(self) -> str:
        return self._render((_SCRIPTS / "codex_agent.sh").read_text())

    def _parse_lines(self, lines: list[str]) -> HarnessRunResult:
        """Parse ``codex exec --json`` output."""
        result = HarnessRunResult()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("type") != "turn.completed":
                continue
            usage = event.get("usage") or {}
            it = (
                usage.get("input_tokens")
                or usage.get("inputTokens")
                or usage.get("prompt_tokens")
                or 0
            )
            ot = (
                usage.get("output_tokens")
                or usage.get("outputTokens")
                or usage.get("completion_tokens")
                or 0
            )
            if isinstance(it, int):
                result.input_tokens += it
            if isinstance(ot, int):
                result.output_tokens += ot
            sr = event.get("stop_reason") or event.get("finish_reason")
            if isinstance(sr, str):
                result.stop_reason = sr
        # Codex does not surface USD; left as None so the prover fills from tokens.
        return result
