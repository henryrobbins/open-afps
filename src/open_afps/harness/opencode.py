"""OpenCode CLI harness."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from open_afps.harness._paths import _SCRIPTS
from open_afps.harness.base import AuthSpec, Harness, HarnessRunResult, _infer_provider
from open_afps.harness.bundles import AssetBundle


class OpenCodeHarness(Harness):
    """OpenCode CLI, authenticated by a provider API key forwarded from the host."""

    name = "opencode"

    def __init__(
        self,
        model: str,
        effort: str = "medium",
        provider: str | None = None,
        assets: AssetBundle | None = None,
    ) -> None:
        super().__init__(model, effort, assets)
        self.provider = provider or _infer_provider(model)

    def configure_wd(self, wd: Path, prompt: str) -> None:
        super().configure_wd(wd, prompt)
        # opencode.json configures the model provider + MCP server.
        (wd / "opencode.json").write_text(json.dumps(self._opencode_config(), indent=2))
        self._copy_skills(wd, ".agents/skills")

    def _opencode_config(self) -> dict[str, Any]:
        options: dict[str, Any]
        if self.provider == "anthropic":
            options = {
                "thinking": {"type": "adaptive"},
                "output_config": {"effort": self.effort},
            }
        else:
            options = {"reasoningEffort": self.effort}
        return {
            "$schema": "https://opencode.ai/config.json",
            "provider": {self.provider: {"models": {self.model: {"options": options}}}},
            "mcp": {
                "lean-lsp": {
                    "type": "local",
                    "command": ["lean-lsp-mcp"],
                    "enabled": True,
                }
            },
        }

    def auth_spec(self) -> AuthSpec:
        env = [
            key
            for key in (
                "ANTHROPIC_API_KEY",
                "OPENAI_API_KEY",
                "GOOGLE_API_KEY",
                "DEEPSEEK_API_KEY",
            )
            if key in os.environ
        ]
        return AuthSpec(env=env)

    def _agent_command(self) -> str:
        template = (_SCRIPTS / "opencode_agent.sh").read_text()
        return template.replace("<<PROVIDER>>", self.provider).replace(
            "<<MODEL>>", self.model
        )

    def _parse_lines(self, lines: list[str]) -> HarnessRunResult:
        """Parse ``opencode run --format json`` output."""

        def _as_int(x: Any) -> int:
            return x if isinstance(x, int) else 0

        result = HarnessRunResult()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("type") != "step_finish":
                continue
            part = event.get("part") or {}
            tokens = part.get("tokens") or {}
            cache = tokens.get("cache") or {}
            result.input_tokens += (
                _as_int(tokens.get("input"))
                + _as_int(cache.get("write"))
                + _as_int(cache.get("read"))
            )
            result.output_tokens += _as_int(tokens.get("output"))
            c = part.get("cost")
            if isinstance(c, (int, float)):
                result.cost_usd = (result.cost_usd or 0.0) + float(c)
            r = part.get("reason")
            if isinstance(r, str):
                result.stop_reason = r
        return result
