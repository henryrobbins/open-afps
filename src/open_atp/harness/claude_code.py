"""Claude Code CLI harness."""

from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar

from open_atp.harness._paths import _MCP_JSON, _SCRIPTS
from open_atp.harness.base import AuthSpec, Harness, HarnessConfig, HarnessRunResult
from open_atp.harness.catalog import resolve_plugin


class ClaudeCodeHarness(Harness):
    """Claude Code CLI, authenticated by a long-lived ``CLAUDE_CODE_OAUTH_TOKEN``."""

    name = "claude_code"

    skills_dest = ".claude/skills"

    config: ClaudeCodeHarnessConfig

    #: Where plugin dirs are staged in the workdir (the launch script's
    #: ``--plugin-dir`` flags reference this, so the two must agree).
    PLUGINS_DIR = ".plugins"

    def stage(self, wd: Path) -> None:
        super().stage(wd)
        # Project-scope MCP config (passed via --mcp-config) and plugins.
        shutil.copy2(_MCP_JSON, wd / ".mcp.json")
        self._copy_plugins(wd)

    def _resolved_plugins(self) -> list[Path]:
        """``config.plugins`` (names or paths) resolved to plugin source dirs."""
        return [resolve_plugin(p) for p in self.config.plugins]

    def _copy_plugins(self, wd: Path) -> None:
        """Stage each configured plugin under ``wd/.plugins/<name>``.

        Claude is the only harness that consumes plugins (so they live on
        :class:`ClaudeCodeHarnessConfig`, not the shared skills list); the launch script
        loads them with ``--plugin-dir`` (see :meth:`_plugin_flags`). Plugins are copied
        *into* the workdir (not referenced from the host vendor tree) so they sync
        into the sandbox with everything else.
        """
        for plugin in self._resolved_plugins():
            shutil.copytree(
                plugin, wd / self.PLUGINS_DIR / plugin.name, dirs_exist_ok=True
            )

    def _plugin_flags(self) -> str:
        """``--plugin-dir`` flags (one per plugin) appended to the launch command.

        Empty when no plugins; otherwise a leading line-continuation so it grafts
        onto the end of the ``claude -p ...`` invocation.
        """
        return "".join(
            f" \\\n    --plugin-dir {self.PLUGINS_DIR}/{p.name}"
            for p in self._resolved_plugins()
        )

    def static_env(self) -> dict[str, str]:
        # Lets bypassPermissions run non-interactively in the container.
        env = {"IS_SANDBOX": "1"}
        # Plugin-provided subagents (e.g. lean4's sorry-filler-deep) are only
        # dispatchable in a headless `-p` run with subagent forking enabled.
        if self.config.plugins:
            env["CLAUDE_CODE_FORK_SUBAGENT"] = "1"
        return env

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
        template = self._render((_SCRIPTS / "claude_code_agent.sh").read_text())
        return template.replace("<<PLUGIN_FLAGS>>", self._plugin_flags())

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


@dataclass
class ClaudeCodeHarnessConfig(HarnessConfig):
    """:class:`~open_atp.harness.base.HarnessConfig` for the Claude Code CLI.

    Claude Code is the only harness that loads plugins, so they live here rather than
    on the prover's shared skills list.

    Attributes
    ----------
    plugins : list[str]
        Claude Code plugins to load, each a name (resolved from the vendored
        ``lean4-skills`` catalog) or a full path to a ``.claude-plugin/plugin.json``
        tree. Default ``["lean4"]``; an empty list loads none.
    """

    plugins: list[str] = field(default_factory=lambda: ["lean4"])
    harness_cls: ClassVar[type[Harness]] = ClaudeCodeHarness
