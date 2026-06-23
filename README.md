# open-afps

[![CI](https://github.com/henryrobbins/open-afps/actions/workflows/ci-python.yml/badge.svg)](https://github.com/henryrobbins/open-afps/actions/workflows/ci-python.yml)
[![codecov](https://codecov.io/gh/henryrobbins/open-afps/branch/main/graph/badge.svg?flag=src)](https://codecov.io/gh/henryrobbins/open-afps)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Docs](https://readthedocs.org/projects/open-afps/badge/?version=latest)](https://open-afps.readthedocs.io/en/latest/)

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

## Status: two compute backends + Aristotle + AgentProver + NuminaProver done

`DockerBackend` and `ModalBackend` both run the shared `Verifier` and the agentic
provers end-to-end against the Mathlib image; the AristotleProver, AgentProver
(claude/codex/opencode + lean-lsp-mcp), and NuminaProver (claude_code + vendored
Numina assets + round loop) are implemented. Docker bind-mounts the workdir; Modal
pushes/pulls it around an isolated Sandbox filesystem. Docker uses `images/Dockerfile`
(runs as the `agent` user); Modal runs as root, so its image is built
programmatically with the same toolchain installed globally (`build-modal-image`).

```bash
# Build the Mathlib base image (pins Lean/Mathlib v4.28.0).
docker build -t open-afps:latest images/

# Run the phase-1 verifier test (compiles a trivial Mathematics-in-Lean file).
uv run pytest -m docker

# Modal backend: publish the same image to Modal, then run its parity suite.
uv run open-afps build-modal-image --name open-afps --app open-afps
uv run pytest -m modal   # needs MODAL_TOKEN_ID / MODAL_TOKEN_SECRET

# Pick a backend (or split: Modal for generation, Docker for the cheap verify).
uv run open-afps solve path/to/project --provers agent --backend modal
uv run open-afps solve path/to/project --provers agent \
    --agent-backend modal --backend docker
```

```python
from open_afps.core.task import LeanProject
from open_afps.core.verifier import docker_verifier

report = docker_verifier().verify(LeanProject("path/to/lake/project"))
print(report.verified, report.sorry_free, report.axioms)
```

### Build order

1. ~~**Backend + verifier (the spine).**~~ ✅ Done: `DockerBackend` and `ModalBackend`
   both ported from milp_flare. `images/Dockerfile` builds the Docker (agent-user)
   image with a warm olean cache; `build-modal-image` builds the root/global Modal
   image programmatically from the same skeleton. `Verifier` compiles file-by-file
   and checks sorry/axioms.
2. ~~**AristotleProver.**~~ ✅ Done: submits the lake project via `aristotlelib`
   (submit → wait → download), unpacks the result over the workdir, and funnels it
   through the shared Docker verifier. Needs `ARISTOTLE_API_KEY` for real runs; tests
   stub the remote call and verify a real proof locally.
3. ~~**AgentProver.**~~ ✅ Done: ports milp_flare's `harness/` (claude/opencode/codex
   + lean-lsp-mcp, `cost.py`) onto the backend with a generic "fill the sorrys" prompt.
   The agent edits the staged project in place; `prove` diffs the `.lean` files and the
   shared verifier does the final check. Needs `CLAUDE_CODE_OAUTH_TOKEN` (or a provider
   key) for real runs; the fast tests mock the launch and parse a captured stream.
4. ~~**NuminaProver.**~~ ✅ Done: vendors Numina's `skills/`+`prompts/` (see
   `vendor/numina/VENDOR.md`) as a selectable asset bundle, extends `AgentProver`
   pinned to `claude_code` with the round-continuation loop (continue while the
   coordinator reports `END_REASON:LIMIT`, stop on `COMPLETE`/`max_rounds`) and the
   ported statement tracker (`numina_tracker.py`) guarding against weakened/deleted
   theorems. Helper-skill API keys (Gemini/OpenAI/Leandex/Anthropic) forward into the
   sandbox; the image pre-warms a uv cache for the skills' PEP 723 deps. Needs
   `CLAUDE_CODE_OAUTH_TOKEN` + `GEMINI_API_KEY` for real runs (`pytest -m numina_api`).
5. ~~**Common API surface**~~ ✅ Done (`api.py`): a `Platform` + prover registry that
   takes a lake project (or bare `.lean` files, staged into the pinned skeleton) and a
   list of provers, builds each from `name → (ProverClass, ConfigClass)` with the
   shared image/backends, fans them out concurrently (`ThreadPoolExecutor`, isolated
   `runs/<id>/<prover>/` workdirs), isolates per-prover failures, and returns a
   `SolveResult` with `verified()`/`best()` (verified → cheapest → fastest) +
   `total_cost_usd` and `to_dict()` JSON. Driven by the `open-afps solve <project>
   --provers aristotle,agent,numina [--json]` CLI. The verify/generation backend split
   is wired across both backends (`--backend`/`--agent-backend`, e.g. Modal for
   generation + local Docker for the cheap verify).

## Layout

```
src/open_afps/
  api.py     Platform + prover registry (the dispatch/orchestration layer)
  __main__.py  `open-afps solve` / `build-image` / `build-modal-image` CLI
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
