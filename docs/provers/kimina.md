(prover-kimina)=
# KiminaProver

The {class}`~open_afps.provers.kimina.KiminaProver` wraps Moonshot AI's
[Kimina-Prover](https://github.com/MoonshotAI/Kimina-Prover-Preview) — an RL-trained,
reasoning-driven model that emits a **complete Lean 4 proof** from a theorem statement,
with *no* external tree search. Unlike the hosted [AristotleProver](aristotle.md), the
model is one **we serve ourselves on GPU compute via vLLM**.

Structurally it is the Aristotle path (generate → splice → verify): for each
`sorry`'d target we prompt the model, splice the returned proof body over the `sorry`,
and let the shared {class}`~open_afps.core.verifier.Verifier` be the authoritative
judge. It runs on the platform's **standard toolchain** — no special Mathlib pin or
toolchain gate — so `kimina` can share one `solve()` call with the other provers.

## How it works

1. **Stage & extract** — the project is staged into the workdir and each `sorry`'d
   `theorem`/`lemma` is located with the shared splice helpers
   ({func}`~open_afps.provers._lean_splice.extract_theorems`), yielding its formal
   statement (ending in `by`) and the character span of the proof body to fill.
2. **Generate** — {meth}`~open_afps.provers.kimina.KiminaProver._generate` produces
   `pass_k` candidate proof bodies per target on the GPU generation backend. Each
   target's preceding doc comment (else the task `instructions`) is forwarded as
   informal-problem context in the prompt.
3. **Select by verifying** — each candidate is spliced over the `sorry` and compiled;
   the **first that compiles, is `sorry`-free, and leaves the signature intact** wins
   (this is how `pass@k` is cashed in honestly — our compile is the source of truth,
   never the model's first guess). A statement guard
   ({class}`~open_afps.provers.numina_tracker.StatementTracker`) rejects any candidate
   that would alter a target's signature.
4. **Verify** — the base {class}`~open_afps.core.prover.AutomatedProver` runs the
   final authoritative whole-project check.

## Compute

Generation requires a **GPU backend** (the 7B distill fits on one modern GPU); the
generation step is isolated behind `_generate`, which runs a one-shot
`kimina_generate.py` entrypoint in the backend (loads the model once via vLLM, writes
candidate proofs). The prompt format and sampling defaults are pinned to the
[model card](https://huggingface.co/AI-MO/Kimina-Prover-Preview-Distill-7B) recipe
(system prompt, `# Problem:` / `# Formal statement:` user template,
`temperature=0.6, top_p=0.95`). CPU Docker cannot serve the model — point `kimina` at
a Modal GPU backend. {class}`~open_afps.backends.modal.ModalConfig` exposes a `gpu`
knob (`"A100"`, `"H100"`, …) and a `volumes` map (to persist the model weights / HF
cache across runs rather than baking multi-GB into the image), both passed to the
Sandbox.

### Building the GPU image

The image (`images/kimina.Dockerfile`) bases on the official vLLM image and layers
the platform's standard Lean toolchain + Mathlib cache on top. Publish it to Modal:

```bash
open-afps build-kimina-image          # publishes a Modal image named "kimina"
```

## Usage

```python
from open_afps.backends.docker import DockerBackend, DockerConfig
from open_afps.backends.modal import ModalBackend, ModalConfig
from open_afps.images import DEFAULT_IMAGE, DEFAULT_TOOLCHAIN
from open_afps.provers.kimina import KiminaProver, KiminaProverConfig

verify = DockerBackend(DockerConfig(image=DEFAULT_IMAGE))
generate = ModalBackend(
    ModalConfig(
        image="kimina",  # the published GPU image
        gpu="A100",
        timeout_s=3600,
        volumes={"kimina-hf-cache": "/root/.cache/huggingface"},  # persist weights
    )
)
config = KiminaProverConfig(
    image=DEFAULT_IMAGE,
    supported_toolchain=DEFAULT_TOOLCHAIN,
    pass_k=32,
    temperature=0.6,
    max_tokens=8192,
)
prover = KiminaProver(config, verification_backend=verify, generation_backend=generate)
```

See {class}`~open_afps.provers.kimina.KiminaProverConfig` in the {doc}`../api/provers`
reference for all configuration knobs.

### Model size

The bare `kimina` prover uses the 7B distill. Registry variants select a checkpoint
without hand-wiring config: `kimina:7b` and `kimina:1.5b` (the smaller, faster
distill). Or set `model` on the config directly to any HF id / mounted path.

```python
platform.solve(task, ["kimina:1.5b", "kimina:7b"])  # compare both
```

:::{note}
**Roadmap.** Per-task model load dominates latency today; a persistent vLLM server and
the Kimina Lean Server (for fast in-sandbox pass@k pre-filtering before the
authoritative compile) are planned optimizations.
:::

:::{note}
Kimina is self-served on your own GPU compute, so {class}`~open_afps.core.result.ProofResult`
reports `cost_usd=None`; GPU-seconds and `pass@k` selection details surface in the run
metadata instead.
:::
