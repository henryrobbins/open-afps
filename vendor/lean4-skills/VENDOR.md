# Vendored: lean4-skills (the `lean4` plugin)

A pinned snapshot of the **lean4-skills** Claude Code plugin marketplace, vendored
so the Claude Code harness can install the `lean4` plugin into the agent workdir
for a single headless run -- fully reproducible, no user/global install.

Unlike `leanprover-skills` (plain host-agnostic skills mounted into every
harness), this is a *Claude-Code plugin*: it ships slash commands, subagents,
and hooks (a `SessionStart` bootstrap that sets the env vars its skill needs).
Only the Claude harness can consume it; the other harnesses use the plain skills.

## Provenance

- Upstream: https://github.com/cameronfreer/lean4-skills (Apache-2.0)
- Copied from commit: `918e80819f460a84001ed771872b1449272476af`
- License: Apache-2.0 (see `LICENSE`)

## What was copied

- `.claude-plugin/marketplace.json` -> upstream, **trimmed** (see drift below)
- `plugins/lean4/`                  -> upstream `plugins/lean4/` verbatim (the
  plugin: `.claude-plugin/plugin.json`, `commands/`, `agents/`, `hooks/`,
  `skills/`, `lib/`, `scripts/`, `tools/`)
- `LICENSE`                         -> upstream `LICENSE`
- `UPSTREAM_README.md`              -> upstream `README.md` (attribution / docs)

## Adaptations applied at copy time (deliberate, reviewable drift)

1. **Dropped the `lean4-contribute` plugin.** Upstream's `marketplace.json` also
   lists a `lean4-contribute` plugin whose commands draft and submit GitHub
   issues (sharing proof snippets with GitHub). That has no place in an
   autonomous eval sandbox, so it is neither vendored nor referenced -- the
   `plugins` array in `marketplace.json` was trimmed to just `lean4`.

## Re-syncing with upstream

1. `git diff` `plugins/lean4/` against the recorded SHA (should be empty -- we
   vendor it verbatim).
2. Pull the new upstream revision, re-copy `plugins/lean4/` + `LICENSE`, re-apply
   the `marketplace.json` trim, bump the SHA.
