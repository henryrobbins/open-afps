#!/usr/bin/env bash

# $PROMPT is exported by the AgentProver before this script runs (it reads
# agent_prompt.txt from the workdir). The backend has already cd'd into the
# workdir and symlinked .lake to the warm Mathlib cache.
#
# bypassPermissions skips all permission prompts (safe in the container);
# IS_SANDBOX=1 (set by the prover) lets that mode run non-interactively.
# .mcp.json registers the lean-lsp MCP server; --strict-mcp-config restricts
# the agent to exactly those servers. The stream-json event stream goes to stdout.
#
# The harness appends zero or more `--plugin-dir .plugins/<name>` flags below (one
# per mounted plugin, staged under .plugins/<name>); --plugin-dir is the only way
# to load a local plugin in a headless `-p` run, and its SessionStart hooks +
# subagents fire there. None are appended when the bundle mounts no plugins.
#
# https://code.claude.com/docs/en/cli-reference
# https://code.claude.com/docs/en/mcp#project-scope

claude -p "$PROMPT" \
    --output-format stream-json --verbose \
    --permission-mode bypassPermissions \
    --mcp-config .mcp.json --strict-mcp-config \
    --model '<<MODEL>>' --effort '<<EFFORT>>'<<PLUGIN_FLAGS>>
