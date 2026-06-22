# Vendored: numina-lean-agent

The `skills/` and `prompts/` directories here are copied from the upstream
**numina-lean-agent** project and adapted for open-afps. Numina's value for this
project is its skills + prompt toolkit (the actual proving "product"); we deliberately
do **not** vendor its `scripts/runner.py` -- that orchestration is re-implemented by
`open_afps.provers.numina.NuminaProver` on top of our own `AgentProver` + backend.

## Provenance

- Upstream: numina-lean-agent (MIT License)
- Local reference at copy time: `/Users/hwr/research/flare/numina-lean-agent`
- Copied from commit: `TODO: record the upstream commit SHA when assets are copied`
- License: MIT (see LICENSE below)

## What was copied

- `skills/`        -> from upstream `skills/` (lean_check, leanexplore, informal_prover, ...)
- `prompts/`       -> from upstream `prompts/autosearch/` (coordinator, proof_agent, ...)

## What was re-implemented instead of copied

- The round-continuation loop (was `scripts/runner.py`) -> `NuminaProver.prove`.
- Statement-change guarding (was `scripts/statement_tracker.py`) -> ported as a
  utility; record its source path/SHA when ported.

## Re-syncing with upstream

These assets will drift as we adapt prompts. To re-sync deliberately:
1. `git diff` our copy against the recorded upstream SHA.
2. Pull the new upstream revision, re-apply our adaptations, bump the SHA above.

## LICENSE

```
TODO: paste upstream MIT LICENSE text here on first copy.
```
