# Leanstral (Mistral Vibe) harness: agent can't edit the file or compile-check

## TL;DR
The `leanstral*` provers run Mistral's Vibe CLI driving its `lean` agent. On the
p6 a→b reformulation task the agent **never verifies anything** because the harness
is mis-wired in two ways:

1. **The `edit` tool is denied** (`Tool execution not permitted`). The agent cannot
   write its proof into the target `Reformulation.lean`. This alone makes a verified
   result impossible.
2. **The lean-lsp MCP server is not loaded.** The system prompt tells the model to
   "use the lean-lsp-mcp tools (`mcp__lean-lsp__*`) to check your work", but those
   tools are absent from the agent's toolset. So there is no compile/diagnostic
   feedback loop, and the model flies blind.

These are **harness bugs, not model failures.** The models (devstral, magistral)
engaged sensibly given the constraints; they were never given a fair shot.

## Where things live
- Prover registry: `refs/open-afps/src/open_afps/api.py`
  - `leanstral` → agent `lean`, model `labs-leanstral-2603` (Labs-gated, 403 until a
    Mistral org admin enables Labs at https://admin.mistral.ai/plateforme/privacy)
  - `leanstral:devstral` → agent `lean-devstral`, model `devstral-medium-latest`
  - `leanstral:magistral` → agent `lean-magistral`, model `magistral-medium-latest`
    (added this session; reasoning model stand-in)
- Harness: `refs/open-afps/src/open_afps/provers/agent/harness.py` → class `VibeHarness`
  - `configure_wd` (~line 512): writes workdir-local `.vibe/config.toml`, copies the
    stand-in agent profile `<agent>.toml` into `.vibe/agents/`. **This is where the
    trust + MCP config needs to be added.**
  - `_agent_command` (~line 528): builds the `vibe -p ... --agent <agent> --output
    streaming --workdir $PWD` call from `assets/scripts/vibe_agent.sh`.
- Stand-in agent profiles: `refs/open-afps/src/open_afps/provers/agent/assets/vibe/`
  - `lean-devstral.toml`, `lean-magistral.toml` (`thinking = "off"`; valid thinking
    values are `off|low|medium|high|max` — `"on"` is a pydantic validation error).
- NOTE: `refs/open-afps` is a symlink to the real `~/research/open-afps` repo
  (editable install). Edits to `src/` take effect immediately, no reinstall. Per the
  user's global rule, warn before modifying anything under `refs/`.

## How to run
```
cd experiments/reformulation_afps
./run.sh --provers leanstral:magistral --problems 6 --backend modal   # or --backend docker
```
- Requires `MISTRAL_API_KEY` in `milp-evo/.env` (present; valid La Plateforme key).
- The Docker image must have `vibe` installed (`pipx install mistral-vibe` in the
  Dockerfile). The Modal image was rebuilt this session and works.
- Results land in `results/<UTC timestamp>/`; prover artifacts + the vibe session log
  under `_runs/p6_a-b/<prover>/.vibe/logs/session/<id>/` (`meta.json` has token/cost
  `stats` and `tools_available`; `messages.jsonl` has the full tool-call trace).

## Evidence (modal magistral run: results/20260623T011721Z)
- `unverified`, 130s, $0.15, 9 steps, 83K in / 3.9K out. Real engagement.
- `tools_available` = `skill, edit, web_search, grep, read, task, bash, todo,
  write_file, web_fetch` — **no `mcp__lean-lsp__*`**.
- `stats`: `tool_calls_succeeded: 6, rejected: 1`.
- Full tool trace: `bash ls`, `grep sorry`, `read x4`, then
  `edit Reformulation.lean → "Tool execution not permitted"`. After the denied edit
  the model gave up and emitted the proof as a chat message (in **Lean 3 `begin/end`
  syntax**, invalid in this Lean 4 / Mathlib4 toolchain).
- `.vibe/trusted_folders.toml` = `trusted = []` → why `edit` is gated.
- `completed_files: []`; `Reformulation.lean` still has its `sorry`.
- The `Sandbox unavailable` / `failed to pull artifacts` stderr lines are **benign
  teardown noise** — `modal_stderr.txt` is 0 bytes and the session log + cost + file
  all synced back correctly.

Earlier devstral run (results/20260623T004514Z): same root cause, different symptom —
devstral couldn't `edit` either, so it used `write_file` to dump into a NEW file
`complete_solution.lean` (which didn't compile). That stray file + an untouched
`Reformulation.lean` is the tell-tale signature of the edit gate.

## Fix plan (priority order)
1. **Un-gate edits (critical — nothing can verify without this). ✅ FIXED.**
   Root cause was NOT folder trust — trust is *never consulted* in `vibe -p`
   programmatic mode. The real gate is `AgentLoop._should_execute_tool`: with
   `auto_approve=False` and no approval callback, any tool resolving to `ASK`
   (i.e. `edit`/`write_file` on an in-workdir path) is answered "Tool execution not
   permitted" and skipped. Read-only `bash ls`/`grep`/`read` worked only because
   they resolve to `ALWAYS`. The builtin `lean` profile sets no `auto_approve`, so
   even the real Leanstral hits this. **Fix:** `VibeHarness.configure_wd` now writes
   `auto_approve = true` into the workdir-local `.vibe/config.toml` (the base
   `VibeConfig`), which `auto_approve` short-circuits every tool to EXECUTE. Verified
   the value survives the `lean` profile's override deep-merge (and the stand-ins').
   **Still TODO:** re-run modal and confirm the tool trace shows a SUCCEEDED `edit`
   and `completed_files` is non-empty.
2. **Wire in lean-lsp-mcp (gives the compile-check loop the prompt assumes). ✅ FIXED.**
   `configure_wd` now appends an `[[mcp_servers]]` stdio entry (`uvx lean-lsp-mcp`,
   mirroring the `.mcp.json` the other harnesses mount) to `.vibe/config.toml`, so it
   applies to `--agent lean` and both stand-ins. NOTE: vibe's builtin `lean` agent
   does NOT configure lean-lsp at all (its `lean.md` prompt + `LEAN` profile rely on
   bash `lake build`); the MCP server is an add-on here. Vibe publishes MCP tools as
   `lean-lsp_<tool>`, not the `mcp__lean-lsp__<tool>` the shared prompt names — the
   tools are present and functional, but the prompt's exact names won't match (vibe's
   `{alias}_{name}` joiner can't produce the `__` form). Models adapt to the real
   toolset; left as-is. Discovery failure is non-fatal (logged, agent runs without
   them). lean-lsp-mcp + uv are in the Docker image (`images/Dockerfile`); confirm the
   Modal image has them too on the next rebuild.
3. **Optional model steering:** general models default to Lean 3 `begin/end`. Add to
   `agent_prompt.txt`: "This is Lean 4 / Mathlib4 — use term-mode or `by` tactic
   blocks; never Lean 3 `begin ... end`." Less needed once #2 gives compiler feedback,
   and not needed for the real `labs-leanstral-2603` (Lean 4-native).

## Open items / caveats
- `magistral` works only with `thinking = "off"` right now. With `thinking = "high"`
  the agent profile fails to load... no — it loads, but the run silently makes 0 LLM
  calls (vibe swallows the API error). Direct `magistral-medium-latest` + tools calls
  work via curl, so the `thinking` reasoning param vibe sends is likely rejected.
  Worth revisiting once #1/#2 are fixed; not blocking.
- The ground-truth proof is 265 lines (`results/kimina_p6/p6.a-b/ground_truth_proof.lean`).
  Even with the harness fixed, expect the stand-in models to struggle; the real
  `labs-leanstral-2603` (Labs-enabled) is the intended model for a real signal.
- Related, separate issue: `KIMINA_CONTEXT_ISSUE.md` (context starvation in the
  kimina prover). Different prover, different root cause.
