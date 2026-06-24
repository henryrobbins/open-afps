"""Agent harnesses: the *agent* concern composed by ``AgentProver``.

Each harness adapts one agent CLI (Claude Code / Codex / OpenCode / Vibe /
ax-prover) to the sandbox: launch script, credential forwarding, and token/cost
parsing. The *compute* concern (where the command runs, with Lean+Mathlib) lives
in the injected :class:`~open_atp.backends.base.ComputeBackend`.
"""

from open_atp.harness.axprover import AxProverHarness
from open_atp.harness.base import (
    PROMPT_FILE,
    SCRIPT_FILE,
    AuthSpec,
    Harness,
    HarnessRunResult,
)
from open_atp.harness.bundles import (
    BUNDLES,
    DEFAULT_BUNDLE,
    AssetBundle,
    bundle_for_config,
    resolve_bundle,
    resolve_plugin,
    resolve_skill,
)
from open_atp.harness.claude_code import ClaudeCodeHarness
from open_atp.harness.codex import CodexHarness
from open_atp.harness.cost import COST_PER_MTOK, compute_cost_usd
from open_atp.harness.opencode import OpenCodeHarness
from open_atp.harness.vibe import VibeHarness

#: Harness registry selected by ``AgentProverConfig.harness``.
HARNESSES: dict[str, type[Harness]] = {
    h.name: h
    for h in (
        ClaudeCodeHarness,
        CodexHarness,
        OpenCodeHarness,
        VibeHarness,
        AxProverHarness,
    )
}

__all__ = [
    "Harness",
    "HarnessRunResult",
    "AuthSpec",
    "SCRIPT_FILE",
    "PROMPT_FILE",
    "AssetBundle",
    "BUNDLES",
    "DEFAULT_BUNDLE",
    "resolve_bundle",
    "bundle_for_config",
    "resolve_skill",
    "resolve_plugin",
    "ClaudeCodeHarness",
    "CodexHarness",
    "OpenCodeHarness",
    "VibeHarness",
    "AxProverHarness",
    "HARNESSES",
    "compute_cost_usd",
    "COST_PER_MTOK",
]
