(prover-vibe)=
# Vibe / Leanstral

```{include} _meta_vibe.md
:parser: myst
```

The Vibe prover is the {class}`~open_atp.provers.agent_prover.AgentProver` on the
{class}`~open_atp.harness.vibe.VibeHarness` — it drives Mistral
[Vibe](https://docs.mistral.ai/mistral-vibe/)'s builtin `lean` agent in a sandbox.
Vibe's `lean` agent *is* Leanstral (`vibe -p ... --agent lean` pins the model to
`leanstral`; there is no `--model` flag). The shared
{class}`~open_atp.verify.Verifier` does the final compile / sorry / axiom
check. See {doc}`index` for the lifecycle every agent harness shares.

## Authentication

Pass the Mistral La Plateforme key to the harness explicitly:

```python
VibeHarness(mistral_api_key="msk-...")
```

or leave `mistral_api_key` unset (the default) to read it from the host environment.
Either way the harness forwards it into the sandbox as `MISTRAL_API_KEY`, where the
lean agent's provider reads it from the process env. Resolution fails if neither the
explicit key nor the host env var is set.

## The Leanstral stand-in

```{warning}
[Leanstral](https://docs.mistral.ai/models/model-cards/leanstral-26-03) is
deprecated as of **2026-05-22** and is only reachable as a Labs model, which
requires Lab Model access from a Mistral org admin. The bare `lean` profile
therefore returns a `403` for keys without Labs access.
```

Because the `lean` profile is Labs-gated, the harness instead runs the same Lean
scaffold on a non-Labs **reasoning** model any La Plateforme key can reach (default
`magistral-medium-latest`) through a vendored `lean-standin` agent profile. Since Vibe
has no `--model` flag, the harness templates the configured model into the stand-in
profile (`<<MODEL>>`) at `stage` time — so the model is an ordinary knob. Repoint
`agent` to `lean` once Labs access is enabled.

## Usage

```python
from open_atp.backends.docker import DockerBackend
from open_atp.harness import VibeHarness
from open_atp.images import DEFAULT_IMAGE
from open_atp.provers import AgentProver

backend = DockerBackend(image=DEFAULT_IMAGE)
prover = AgentProver(
    harness=VibeHarness(
        agent="lean-standin",            # "lean" once Labs is enabled
        model="magistral-medium-latest",
        max_turns=None,                  # passed to `vibe -p --max-turns`
        max_price=None,                  # passed to `vibe -p --max-price`
    ),
    backend=backend,
)
```

{class}`~open_atp.harness.VibeHarness` selects the Vibe CLI and carries the
Vibe-specific `agent`, `max_turns`, and `max_price` knobs (which live only on this
harness, not the shared base).

Or by catalog name through {func}`~open_atp.config.standard_prover` / the CLI:
`vibe` (defaults: `agent="lean-standin"`,
`model="magistral-medium-latest"`). `standard_prover`
returns this default prover only; to swap the model, construct
`VibeHarness(model="devstral-medium-latest")` and pass it to `AgentProver`
directly (as above).

## Harness details

`stage` pins a workdir-local `VIBE_HOME` (`.vibe/`) so Vibe's config, the
vendored stand-in profile, and the per-session log all live under the workdir and sync
back out with it. The written `.vibe/config.toml`:

- sets `installed_agents = ["lean"]` to un-gate the builtin `lean` agent;
- sets `bypass_tool_permissions = true` — the only way to un-gate mutating tools
  (`edit`, `write_file`) in `vibe -p` programmatic mode, which has no approval
  callback (without it the agent's edits are silently skipped);
- enables `[session_logging]` (where cost/token totals are recorded); and
- wires the lean-lsp MCP server with `tool_timeout_sec = 180` (the seconds-valued
  mirror of the OpenCode 180 s fix, for the cold first `lean_diagnostic_messages`
  call that loads the full Mathlib import closure).

The stand-in profile is written to `.vibe/agents/<agent>.toml`, and the prover stages
the `AgentProver`'s `skills` — the host-agnostic
[`leanprover/skills`](https://github.com/leanprover/skills) — under `.vibe/skills`
(Vibe's user skills dir, which loads regardless of project-folder trust). The launch
script (`assets/scripts/vibe_agent.sh`) runs:

```bash
export VIBE_HOME="$PWD/.vibe"
vibe -p "$PROMPT" --agent <AGENT> --output streaming --workdir "$PWD" <EXTRA>
```

`<EXTRA>` appends `--max-turns` / `--max-price` when set. The `--output streaming`
NDJSON message stream (one message per line) goes to stdout.

`$PROMPT` is the shared agent prover prompt baked into the
{class}`~open_atp.provers.agent_prover.AgentProver`, with the task's optional
`user_prompt` appended under an *Additional instructions* heading when set:

:::{dropdown} Agent prover prompt
:icon: code
```{literalinclude} ../../src/open_atp/provers/agent_prover.py
:language: text
:start-after: PROVER_PROMPT = """
:end-before: END PROVER_PROMPT
```
:::

## Cost tracking

The streaming output carries only conversation messages — no token/cost totals. Those
live in Vibe's per-session `meta.json`; `parse` reads `session_cost`,
`session_prompt_tokens`, and `session_completion_tokens` from its `stats` to populate
`cost_usd` and the token totals in
{class}`~open_atp.harness.base.HarnessRunResult`. `collect_logs` relocates the
`.vibe/logs` tree to `logs/vibe-session`.
