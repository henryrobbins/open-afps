# Plan: add `ax-prover-base` as an agent harness (`agent:axprover`)

## TL;DR
`ax-prover-base` is a LangGraph-based Lean 4 proving agent (own
proposer→builder→reviewer→memory loop, raw provider API keys, edits the target
`.lean` file in place). It has the same *shape* as the agents open-afps already
runs, so it slots in as a new `Harness` in the agent framework rather than as a
standalone prover. The closest existing precedent is `VibeHarness`: a non-generic
agent framework that runs in the sandbox and reads cost from a side-channel file
instead of stdout.

This is **Option A** from the evaluation: add `AxProverHarness` + a launch script
+ a registry entry, reusing all of `AgentProver.prove` (staging, snapshot, backend
run, diff). No architectural changes.

## Why a harness, not a standalone prover
`AgentProver.prove` already does everything ax-prover needs around the edges:

| Concern | Already handled by `AgentProver` / answered by ax-prover |
|---|---|
| stage project into workdir, ignore `.lake`/`.git` | `AgentProver.prove` step 1 |
| snapshot `.lean`, diff after run → `completed_files` | steps 2 + 6 (ax-prover edits in place, so this just works) |
| run a bash command in the sandbox, stream stdout | `_run_agent` + the `ComputeBackend` |
| forward provider API keys into the sandbox | `auth_spec()` (same as `OpenCodeHarness`) |
| independent compile / sorry-free / no-foreign-axiom check | base `run()` → `Verifier` (we do **not** trust ax-prover's own reviewer) |

The only prover-specific pieces are: which command to run, where credentials
come from, and how to read cost. Those are exactly what a `Harness` encapsulates.

## Where things live
- Prover registry / factory: `src/open_afps/api.py` → `REGISTRY`
  - Add `"agent:axprover": _Entry(AgentProver, AgentProverConfig, {"harness": "axprover"})`
- Harness base + registry: `src/open_afps/provers/agent/harness.py`
  - Add `class AxProverHarness(Harness)` and register it in `HARNESSES`
  - **Model on `VibeHarness`** (lines ~450–602): it is the existing precedent for an
    agent whose cost is not on stdout and whose framework is not a generic coding CLI.
- Launch script: `src/open_afps/provers/agent/assets/scripts/axprover_agent.sh` (new)
- Config defaults (model/effort/iterations): a `default.yaml` written into the workdir
  by `configure_wd`, derived from ax-prover's bundled `configs/default.yaml`.
- Sandbox image: `images/Dockerfile` (install `ax-prover` + its stack — see below).
- Reference source: `refs/ax-prover-base/` (symlink; **reference only, do not modify**
  except the one upstream cost-output patch noted below, which we should land in the
  real ax-prover repo, not via `refs/`).

## Implementation steps

### 1. `AxProverHarness` in `harness.py`
```python
class AxProverHarness(Harness):
    """ax-prover-base (LangGraph Lean agent), driven by `ax-prover prove` in-sandbox."""
    name = "axprover"

    def auth_spec(self) -> AuthSpec:
        # Raw provider keys, exactly like OpenCodeHarness. At least one required.
        env = [k for k in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GOOGLE_API_KEY")
               if k in os.environ]
        if not env:
            raise RuntimeError("axprover harness requires one of ANTHROPIC_API_KEY / "
                               "OPENAI_API_KEY / GOOGLE_API_KEY")
        return AuthSpec(env=env)

    def configure_wd(self, wd: Path, prompt: str) -> None:
        super().configure_wd(wd, prompt)          # writes agent.sh + prompt (prompt unused)
        # Write a config.yaml selecting model/effort/max-iterations into the workdir.
        (wd / "axprover.yaml").write_text(self._render_config())

    def _agent_command(self) -> str:
        return self._render((_SCRIPTS / "axprover_agent.sh").read_text())

    def parse(self, lines: list[str]) -> HarnessRunResult:
        # Cost/tokens are NOT on stdout; read the usage side-channel file ax-prover
        # writes into the workdir (see step 3). Mirrors VibeHarness._read_session_stats.
        ...
```
- The free-text `prompt` arg is ignored (ax-prover has its own prompts). That is
  consistent with how `VibeHarness` ignores parts of the contract it does not use.

### 2. `axprover_agent.sh` — self-discover targets, no task plumbing needed
ax-prover needs a *target* (`file.lean:thm`, `file.lean`, or a module), but the
`Harness` contract is project-wide. The script self-discovers, so **no change to
`Harness.configure_wd`'s signature is required**:
```bash
#!/usr/bin/env bash
set -euo pipefail
# Warm .lake is symlinked by the backend; skip ax-prover's own lake build.
for f in $(grep -rl --include='*.lean' '\bsorry\b' . | grep -v '/\.lake/'); do
  ax-prover prove "$f" \
    --config axprover.yaml \
    --folder . \
    --skip-build \
    --overwrite \
    -o "ax_output.$(echo "$f" | tr '/' '_').json" || true
done
```
- `--skip-build` relies on the image's warm Mathlib `.lake` (same assumption the
  other harnesses make); avoids a redundant `lake build`.
- `|| true` so one unprovable file does not abort the rest; the final `Verifier`
  pass is the source of truth either way.

### 3. Cost output — the one real gap (needs a small upstream change)
ax-prover's `-o` JSON is only `{success, error, summary}`; no tokens/cost. Every
other harness reports `cost_usd` or token counts. The LangChain layer has usage
data but does not surface it.
- **Fix:** patch ax-prover's `LLMClient` (`refs/ax-prover-base/src/ax_prover/utils/llm.py`)
  to accumulate token usage and dump it to a file in the run folder (e.g.
  `ax_usage.json`). Land this in the real ax-prover repo, not via `refs/`.
- `AxProverHarness.parse` then reads `ax_usage.json` and fills `input_tokens` /
  `output_tokens`; `compute_cost_usd(model, ...)` converts to USD. Same pattern as
  `VibeHarness.parse` → `meta.json`.
- **Fallback if the upstream patch is deferred:** leave `cost_usd=None` and scrape
  token totals from logs if available. Cost just won't be reported until the patch
  lands.

### 4. Sandbox image (`images/Dockerfile`) — the bulk of the work
Install `ax-prover` and its stack **into the image**, not into open-afps's
`pyproject.toml`. Because it runs inside the sandbox, its heavy deps
(`langgraph`, `langchain-*`, `lean-interact`, `omegaconf`, `tavily`) **never
conflict with the orchestrator** — full isolation.
- Lean toolchain + warm Mathlib `.lake` are already present (what `lean-interact`'s
  local REPL and `--skip-build` need).
- Install ax-prover (pip from a pinned ref/sdist once the cost patch is published).

### 5. Registry + exports
- `api.py`: add the `agent:axprover` `_Entry` (config defaults `{"harness": "axprover"}`,
  plus a default `model`/`effort` appropriate for ax-prover, e.g. Claude Opus with
  thinking).
- `HARNESSES` dict in `harness.py`: register `AxProverHarness`.

## Open questions / risks to confirm
1. **Network egress.** ax-prover's `LeanSearch` tool calls `leansearch.net` and web
   search calls Tavily. Confirm the Docker/Modal sandbox allows outbound network, or
   disable those tools in `axprover.yaml` (they are optional). LLM API calls also need
   egress.
2. **Timeout.** ax-prover defaults to 50 iterations; ensure `config.timeout_s` is
   generous enough, or lower `max_iterations` in `axprover.yaml`.
3. **Per-file vs. whole-project.** The loop above runs ax-prover once per sorry-file.
   If a project has many files, consider ax-prover's module-target mode instead, or a
   standalone-prover (Option B) for Python-level fan-out. Start with the simple loop.
4. **Cost patch ownership.** Step 3 requires a change in the ax-prover repo. Decide who
   lands it before cost tracking is reliable.

## Effort estimate
Low-to-moderate. The harness + script + registry wiring is small and precedented by
`VibeHarness`. The two real costs are (a) adding the LangGraph stack to the sandbox
image and (b) the small upstream ax-prover patch to emit token usage. Network egress
is a config detail to confirm.

## Suggested order
1. Draft `AxProverHarness` + `axprover_agent.sh` + registry entry (clarifies exactly
   what the image and cost file must provide).
2. Land the ax-prover usage-output patch upstream.
3. Update `images/Dockerfile`; build and smoke-test on one sorry-file task end-to-end.
