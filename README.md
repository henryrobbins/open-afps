# open-afps

**Open Automated Formal Proof Synthesis.** Upload one or more Lean files containing
`sorry`, run them through leading proof-synthesis backends, and get back verified
completed proofs with metadata (verification status, cost, duration).

## Core idea

The whole platform reduces to two reusable primitives plus thin candidate generators:

1. **`ComputeBackend`** (`backends/`) — run a command over a working directory in a
   Lean+Mathlib sandbox. Two implementations: `DockerBackend`, `ModalBackend`.
2. **`Verifier`** (`core/verifier.py`) — compile a candidate project in a backend and
   report whether it compiles, is sorry-free, and is axiom-clean.

Every prover funnels its output through the **shared verifier**, including Aristotle.

```
ComputeBackend (docker | modal)         ← the sandbox primitive
        │
        ├── Verifier  ──────────────────← shared final check (ALL provers)
        │
AutomatedProver (base)
 ├── AgentProver      coding agent (claude/opencode/codex) + lean-lsp-mcp in sandbox
 ├── NuminaProver     configured AgentProver: claude + vendored Numina assets + round loop
 └── AristotleProver  remote `aristotle submit --project-dir --wait`, no sandbox to generate
```

## Input contract

Submit a **full lake project** (carries `lean-toolchain` + `lake-manifest.json`). The
verifier **rejects** projects whose toolchain doesn't match the sandbox image's pin
(`ToolchainMismatch`) rather than failing deep in a build. One Mathlib image to start;
`image` is a config field so more can be added without refactoring.

## Status: phase-1 skeleton

The abstractions and wiring exist and import cleanly; backend/prover bodies are stubs
with `TODO`s pointing at the milp_flare / numina source to port from.

### Build order

1. **Backend + verifier (the spine).** Port milp_flare `runner/{docker,modal}.py` into
   `ComputeBackend`; build the Mathlib `images/Dockerfile`; finish `Verifier`. Test on a
   known-good and a known-sorry project across both backends.
2. **AristotleProver.** Cheapest end-to-end slice: wrap the CLI, unpack the tar.gz, verify.
3. **AgentProver.** Port milp_flare's `harness/` (claude/opencode/codex + lean-lsp-mcp,
   `cost.py`) onto the backend; generic "fill the sorrys" prompt.
4. **NuminaProver.** Vendor Numina's `skills/`+`prompts/` (see `vendor/numina/VENDOR.md`),
   extend `AgentProver` with the round-continuation loop + statement tracker.
5. **Common API surface** (`api.py`): files + chosen provers + configs → `ProofResult`s;
   concurrency/job tracking last.

## Layout

```
src/open_afps/
  core/      task.py result.py prover.py verifier.py
  backends/  base.py docker.py modal.py
  provers/   agent.py numina.py aristotle.py
images/      Dockerfile (Mathlib base)
vendor/numina/  vendored skills/prompts + VENDOR.md (MIT, tracked to upstream SHA)
```

## References (read-only symlinks under `refs/`)

- `milp_flare` — harness/runner/verification to port (the agentic + LSP MCP setup).
- `numina-lean-agent` — MIT; vendor its skills/prompts, re-implement the runner.
- `aristotle` — example client for `aristotle submit`.
