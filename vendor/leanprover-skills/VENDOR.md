# Vendored: leanprover/skills

The `skills/` directory here is copied verbatim from the official
**leanprover/skills** repository ("Official Agent Skills for developing with
Lean 4"). These are plain, host-agnostic Agent Skills -- self-contained
`skills/<name>/SKILL.md` methodology guides with no slash commands, hooks,
bootstrap scripts, or required environment variables -- so they mount cleanly
into any harness's skill location (`.claude/skills`, `.agents/skills`,
`VIBE_HOME/skills`) and work under a headless `-p` launch.

`open_afps.harness.bundles` mounts a *subset* of these into the agent workdir
(the default bundle enables `lean-proof`); the rest are vendored so they can be
opted into by name without a re-sync.

## Provenance

- Upstream: https://github.com/leanprover/skills (Apache-2.0)
- Copied from commit: `7d3da0282e7b724b07620e45cf212f2e05e19334`
- License: Apache-2.0 (see `LICENSE`)

## What was copied

- `skills/`            -> upstream `skills/` verbatim (all 10 skills:
  lean-proof, lean-setup, lean-mwe, lean-bisect, lean-pr, mathlib-build,
  mathlib-pr, mathlib-review, nightly-testing)
- `LICENSE`            -> upstream `LICENSE`
- `UPSTREAM_README.md` -> upstream `README.md` (kept for attribution / install
  notes; not used at runtime)

No adaptations were applied -- the skills are vendored unmodified. Each skill's
`tests/` subdirectory is upstream CI fixture data and is excluded when the skill
is mounted into the agent workdir (see `Harness._copy_skills`).

## Re-syncing with upstream

1. `git diff` our copy against the recorded SHA (should be empty -- we vendor
   verbatim).
2. Pull the new upstream revision, re-copy `skills/` + `LICENSE`, bump the SHA.
