# Vendored: numina-lean-agent

The `skills/` and `prompts/` directories here are copied from the upstream
**numina-lean-agent** project and adapted for open-afps. Numina's value for this
project is its skills + prompt toolkit (the actual proving "product"); we deliberately
do **not** vendor its `scripts/runner.py` -- that orchestration is re-implemented by
`open_afps.provers.numina.NuminaProver` on top of our own `AgentProver` + backend.

## Provenance

- Upstream: numina-lean-agent (MIT License)
- Local reference at copy time: `/Users/hwr/research/flare/numina-lean-agent`
- Copied from commit: `e9e987b47f14ef818d5932a11dc026048abc35e7` (2026-04-30)
- License: MIT (declared in upstream `README.md`; upstream ships no `LICENSE`
  file, so the standard MIT text is reproduced below with attribution to the
  upstream authors).

## What was copied

- `skills/`   -> from upstream `skills/` (lean_check, leanexplore, informal_prover, ...)
- `prompts/`  -> from upstream `prompts/autosearch/` (main_entry, coordinator, proof_agent, ...)

## Adaptations applied at copy time (deliberate, reviewable drift)

1. **Skill location.** Numina invoked its CLI scripts from the project-root
   `skills/cli/`. open-afps stages this bundle into the agent workdir's
   `.claude/skills/` (Claude Code skill discovery), so every `skills/...`
   reference in the vendored markdown was rewritten to `.claude/skills/...`, and
   `prompts/autosearch/subagent_prompts/` to `.claude/prompts/subagent_prompts/`
   (where `NuminaProver` stages the coordinator/subagent prompts).
2. **Invocation via uv.** The helper skills are `#!/usr/bin/env python3` scripts
   that need third-party packages (`requests`, `google-genai`, `openai`,
   `anthropic`). Rather than bake a venv, the four scripts that need them carry
   PEP 723 `# /// script` inline dependency blocks, and all markdown invocations
   were rewritten from `python skills/cli/<tool>.py` to
   `uv run --no-project .claude/skills/cli/<tool>.py` (uv is on the image PATH and
   its cache is pre-warmed with these deps in `images/Dockerfile`).

Only the markdown docs/prompts and the four skill headers were touched; the Python
skill logic is byte-for-byte upstream.

## What was re-implemented instead of copied

- The round-continuation loop (was `scripts/runner.py`) -> `NuminaProver.prove`.
- Statement-change guarding (was `scripts/statement_tracker.py` +
  `scripts/extract_sublemmas.py`) -> ported to
  `src/open_afps/provers/numina_tracker.py` (same upstream SHA as above).

## Re-syncing with upstream

These assets will drift as we adapt prompts. To re-sync deliberately:
1. `git diff` our copy against the recorded upstream SHA.
2. Pull the new upstream revision, re-apply the adaptations above, bump the SHA.

## LICENSE

```
MIT License

Copyright (c) 2026 Numina (numina-lean-agent authors)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
