(prover-numina)=
# NuminaProver

```{include} _meta_numina.md
:parser: myst
```

The {class}`~open_atp.provers.numina.NuminaProver` is a configured variant of the
{class}`~open_atp.provers.agent_prover.AgentProver`. Structurally, Numina is
"Claude Code + a specific skills/prompts/search toolkit, run in a multi-round loop in
a sandbox", so rather than re-implement it, `open-atp` extends `AgentProver` pinned
to the `claude_code` harness with Numina's vendored assets and adds the two genuinely
different behaviours:

- a **round-continuation loop** — re-invoke the agent while it reports it hit a limit
  rather than completing; and
- the **statement tracker** — guard against the agent deleting or weakening the
  theorems it was asked to prove.

The shared {class}`~open_atp.verify.Verifier` does the final compile / sorry / axiom
check. See {doc}`index` for the lifecycle every agent harness shares.

## Authentication

Numina runs on the Claude Code CLI, so it authenticates exactly like the
{doc}`claude_code` prover. Generate a long-lived OAuth token once on the host:

```bash
claude setup-token
```

`NuminaProver` exposes no `oauth_token` knob — it reads `CLAUDE_CODE_OAUTH_TOKEN`
from the host environment (for example a `.env` file in your project) and forwards it
into the sandbox, billing against your Claude plan rather than the API.

Numina's helper skills additionally call out to Leandex / Gemini / GPT (and Claude
for the informal prover). Their keys — `LEAN_LEANDEX_API_KEY`, `GEMINI_API_KEY`,
`OPENAI_API_KEY`, and `ANTHROPIC_API_KEY` — are forwarded into the sandbox
best-effort when present in the host env; a skill whose key is absent degrades or
skips rather than failing the run.
{attr}`~open_atp.provers.numina.NuminaProver.helper_env_keys` selects which keys are
forwarded.

## Usage

```python
from open_atp.backends.docker import DockerBackend
from open_atp.images import DEFAULT_IMAGE
from open_atp.provers.numina import NuminaProver

backend = DockerBackend(image=DEFAULT_IMAGE)
prover = NuminaProver(
    backend=backend,
    max_rounds=20,
    guard_statements=True,
)
```

The harness is fixed to `claude_code` and assets to `numina`. See
{class}`~open_atp.provers.numina.NuminaProver` in the {doc}`../api/provers`
reference for the full set of fields.

Or by catalog name through {func}`~open_atp.config.standard_prover` / the CLI:
`numina`.

## Harness details

The harness is pinned to an internal `NuminaHarness` — Claude Code with **no
plugins**, since Numina ships its own scaffold — and is not configurable. Rather
than wire skills through the shared bundle, `_stage_numina_assets` mounts Numina's
vendored scaffold (`vendor/numina/skills` + `vendor/numina/prompts`) straight into
the known `.claude/` locations: the coordinator skill's contents at `.claude/skills`
and the subagent-prompt tree at `.claude/prompts`.

Two behaviours differ from a plain agent run:

- **Round-continuation loop.** Each round is a fresh `claude -p` invocation over the
  same persistent workdir; the loop re-invokes the agent while it reports
  `END_REASON:LIMIT` (made progress but ran out of turns/budget) and stops on
  `END_REASON:COMPLETE`, up to `max_rounds`. `max_consecutive_limits` triggers a
  session reset after that many LIMIT rounds in a row.
- **Statement tracker.** When `guard_statements` is set, the target theorems are
  snapshotted before the run; if a round weakens or deletes one, the originals are
  restored and (with `on_statement_change="error"`, the default) the run stops.

`$PROMPT` is Numina's coordinator scaffold (`main_entry.md`) plus an explicit
session-control protocol so the loop can tell "done" from "out of budget", with the
task's optional `user_prompt` appended under an *Additional instructions* heading
when set:

:::{dropdown} Round-control protocol (appended to Numina's coordinator prompt)
:icon: code
```{literalinclude} ../../src/open_atp/provers/numina.py
:language: text
:start-after: _END_REASON_PROTOCOL = """
:end-before: '"""'
```
:::

## Cost tracking

The Claude Code CLI reports per-round USD directly, summed across rounds into the
agent's cost. On top of that, the `discussion_partner` skill (Gemini/GPT) appends a
per-call token-usage record to a workdir ledger (`.claude/helper_usage.jsonl`);
after the run `prove()` prices it via the {mod}`~open_atp.harness.cost` table and
folds it into `cost_usd`, so the reported cost includes discussion-partner spend
rather than only the Claude agent. The split is preserved in metadata
(`agent_cost_usd`, `helper_cost_usd`, `helper_breakdown`). Helper models absent from
the price table are billed at `0` but surfaced in `helper_unpriced_models` so the gap
is visible — the `gpt-5.4-pro` / `gemini-3.1-pro-preview` defaults carry
**estimated** prices that should be verified against the provider pricing pages.
