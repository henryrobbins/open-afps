# Handoff: KiminaProver (whole-proof generation prover)

Add Moonshot AI's **Kimina-Prover Preview** as a registered prover (`kimina`). It is a
whole-proof generation model (RL-trained Qwen2.5, reasoning-driven — *no* external tree
search), open-released as distilled 1.5B / 7B checkpoints. miniF2F-test: 80.74%
pass@8192, 68.85% pass@32.

We chose this over BFS-Prover-V2 as the first open-weights prover because it integrates
with **far less risk**: whole-proof generation maps almost directly onto our existing
contract — no LeanDojo, no repo tracing, no fixed-commit requirement, no Lean-4.10.0
toolchain lock, no Ray/tree-search machinery. (See `BFS_PROVER_PLAN.md` for the harder
path we deferred.)

## Why this fits our contract nearly as-is

Our prover contract (`core/prover.py`, `core/task.py`):

> **input** = a lake project carrying `sorry`s → **output** = completed `.lean` files →
> the shared `Verifier` compiles them in our sandbox.

Kimina takes a **theorem statement** and emits a **complete Lean 4 proof**. So the
adapter is short: for each `sorry`'d target, prompt the model, splice the returned proof
over the `sorry`, and let our `Verifier` be the source of truth. Structurally this is
`AristotleProver` (call model → get proof → splice → verify), except the "model" is one
**we serve ourselves on a GPU via vLLM** instead of a hosted API — which reuses the
exact GPU-`ModalBackend` knob the BFS plan already specified, and *nothing else* from it.

### Input / output (from the model card)
- **Serving:** vLLM (explicitly recommended).
- **Prompt:** system `"You are an expert in mathematics and Lean 4."`; user = an
  (optional) informal problem statement + the **formal Lean 4 statement** ending in `by`.
  *Pin the exact chat template from `AI-MO/Kimina-Prover-Preview-Distill-7B` during
  implementation — don't hard-code it from memory.*
- **Output:** interleaved reasoning + Lean code blocks; the final proof is the tactic
  block after `by`. Extract the last/complete Lean code block → the proof body.
- **pass@k:** quality scales hard with samples. Generate K candidates per theorem and
  take the first that **verifies** (don't just trust the first sample).

## Design

`KiminaProver(AutomatedProver)`, `name = "kimina"`, `src/open_afps/provers/kimina.py`.
`prove(task, workdir)`:

1. **Stage** project into `workdir`; snapshot original `.lean` (same prologue as
   Aristotle/Agent, `_IGNORE` `.lake/.git`).
2. **Extract targets** → `(full_name, statement, sorry_span)` per `sorry`'d theorem
   (`task.resolved_targets()`).
3. **Generate** K candidate proofs per target by running a small generation entrypoint
   on GPU compute (vLLM loads the model, takes statements jsonl, returns candidates
   jsonl). Behind a `_generate(statements) -> dict[name, list[str]]` seam for testing.
4. **Select by verifying.** For each target, splice each candidate into the workdir file
   and compile via the shared `Verifier`; keep the **first that verifies** (`sorry`-free,
   axiom-clean). This is how we cash in pass@k and stay honest — our compile is
   authoritative. Leave the file on the winning candidate (or original if none pass).
5. **Diff** workdir `.lean` vs snapshot → `completed_files`; return `GenerationOutput`
   with `cost_usd=None` (self-served; surface GPU-seconds + `pass@k`, `samples_tried`,
   per-target winning index / None in metadata).

**Statement guard:** the model regenerates the whole `theorem … := by …` block, so guard
that it didn't alter the *signature* — only the proof body may change. Reuse the
`numina_tracker.py` `StatementTracker` approach; reject/restore on signature drift.

### Splicing — shared with the BFS plan
`extract_theorems(lean_text) -> [(name, statement, sorry_span)]` and
`splice_proof(lean_text, sorry_span, proof) -> str` are the same pure, unit-tested
helpers the BFS plan called for. Build them **provider-agnostic** here (e.g.
`provers/_lean_splice.py`) so both provers share them.

## Compute: GPU via vLLM

`ModalConfig` gains `gpu: str | None = None`; pass `gpu=` to `Sandbox.create` (Modal
takes `"A100"`, `"H100"`, …; see `.agents/skills/modal/references/guide/gpu.md`). The
7B distill fits on one modern GPU. Docker stays CPU; document that `kimina` requires a
GPU backend and error clearly if pointed at CPU Docker.

**Serving shape — recommend one-shot over a server.** Bake a tiny `kimina_generate.py`
into the image: reads a statements jsonl, loads the model once with vLLM, generates K
samples with `SamplingParams`, writes a candidates jsonl. The prover invokes it via
`ComputeBackend.start(command)` and pulls the result — matching our command-oriented
backend with no second process to manage. (A persistent vLLM OpenAI server is a Phase-C
optimization if per-task model-load latency hurts.)

## Image (Phase B)

A dedicated GPU image, separate from `images/Dockerfile`: CUDA base → `pip install vllm`
→ install Lean + Mathlib (our **standard** toolchain — Kimina has no LeanDojo/4.10.0
pin, a big simplification over BFS) → fetch the model (mount a Modal **Volume** for the
weights rather than baking multi-GB; `.agents/skills/modal/references/guide/model-weights.md`).
Publish via the same `build-modal-image` CLI path the Modal handoff added to
`src/open_afps/__main__.py` (`open-afps build-kimina-image`).

## Phasing

- **Phase A — adapter, generation stubbed.** Prover + config + registry + the shared
  splice helpers + statement guard, with `_generate` behind a test seam returning canned
  proofs. Fully offline-testable (no GPU/model/network), mirroring the Aristotle stub and
  `test_modal_backend.py`. **Do first** — it's most of the new code.
- **Phase B — GPU + image.** `ModalConfig.gpu`, the BFS-style image, `kimina_generate.py`,
  one real miniF2F theorem end-to-end asserting `Verifier.verified`.
- **Phase C — optimizations.** Persistent vLLM server; the Kimina Lean Server for fast
  in-sandbox pass@k filtering before the authoritative final compile; 1.5B vs 7B vs the
  full preview model as a config knob; informal-problem context in the prompt.

## Config + registry

```python
@dataclass
class KiminaProverConfig(AutomatedProverConfig):
    model: str = "AI-MO/Kimina-Prover-Preview-Distill-7B"  # HF id or mounted path
    pass_k: int = 32
    temperature: float = 0.6
    max_tokens: int = 8192
    gpu: str = "A100"
    guard_statements: bool = True

# api.py REGISTRY
"kimina": _Entry(KiminaProver, KiminaProverConfig, {"image": KIMINA_IMAGE}),
```

Unlike BFS, Kimina runs on our **standard toolchain**, so it does **not** trip the
`Platform.solve` global toolchain gate — `kimina` can share one `solve()` call with
AgentProver/Aristotle. No gate changes needed. (Confirm the distill model proves on the
platform's Mathlib revision; it was trained on a specific Mathlib pin — worth a smoke
test, but it does not force a different toolchain the way BFS does.)

## Testing

- **Pure helpers:** `extract_theorems` / `splice_proof` over fixture `.lean` text.
- **`prove` with `_generate` stubbed:** canned candidates incl. a non-compiling one
  first → assert pass@k selection lands on the verifying candidate and `completed_files`
  reflects it; assert the statement guard rejects a signature change.
- **One real end-to-end** (Phase B, marked slow): a miniF2F theorem on a Modal GPU
  sandbox → `Verifier` reports `verified`.

## Files to touch

- **new** `src/open_afps/provers/kimina.py` — `KiminaProver`, `KiminaProverConfig`.
- **new** `src/open_afps/provers/_lean_splice.py` — shared extract/splice helpers.
- `src/open_afps/api.py` — registry entry (no toolchain-gate change).
- `src/open_afps/backends/modal.py` — `ModalConfig.gpu` + pass to `Sandbox.create`.
- `src/open_afps/__main__.py` — `build-kimina-image` (Phase B).
- **new** `images/kimina.Dockerfile` + `kimina_generate.py` (Phase B).
- **new** `tests/test_kimina_prover.py`.
- `docs/provers/…` — a Kimina page.

## Open questions

1. **Exact chat template** — read it off the model card, don't guess.
2. **Mathlib revision** the distill was trained against vs our platform pin — smoke-test
   proof success; likely fine, not a hard toolchain lock.
3. **pass@k cost** — K authoritative compiles per theorem. Phase-C Lean-server
   pre-filtering reduces this; for v1 keep K modest (≈8–32) and log it.
4. **Weights delivery** — Volume mount vs bake; GPU type / count drive cost.
```
