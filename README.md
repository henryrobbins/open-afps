<p align="center">
  <img src="docs/_static/logo_light.svg" alt="OpenATP" width="420">
</p>

[![CI](https://github.com/henryrobbins/open-atp/actions/workflows/ci-python.yml/badge.svg)](https://github.com/henryrobbins/open-atp/actions/workflows/ci-python.yml)
[![codecov](https://codecov.io/gh/henryrobbins/open-atp/branch/main/graph/badge.svg?flag=src)](https://codecov.io/gh/henryrobbins/open-atp)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Docs](https://readthedocs.org/projects/open-atp/badge/?version=latest)](https://open-atp.readthedocs.io/en/latest/)

`OpenATP` (Open Automated Theorem Proving) runs Lean files containing `sorry`
through leading proof-synthesis backends and returns **verified** completed
proofs with metadata (verification status, cost, duration). Every prover —
including hosted ones like Aristotle — funnels its output through one shared
`Verifier` that compiles the candidate in a Lean+Mathlib sandbox and checks that
it compiles, is sorry-free, and is axiom-clean. See the
[documentation](https://open-atp.readthedocs.io) for details.

## Installation

```bash
pip install open-atp
```

`OpenATP` runs each agent harness (e.g., Claude Code, Codex, OpenCode) in a
Docker container. The image must be built before running any prover:

```bash
open-atp build-image
```

Each harness has its own authentication requirements, and the hosted provers
need their own API keys. See [Installation](https://open-atp.readthedocs.io/en/latest/installation.html)
for more details.

## Quickstart

Complete the `sorry`s in a lake project (or bare `.lean` files) from the CLI:

```bash
open-atp solve path/to/project --provers agent --backend docker
```

Or programmatically, here on a bundled example:

```python
import tempfile

from open_atp import standard_prover
from open_atp.backends import DockerBackend
from open_atp.examples import EXAMPLE, example_task

prover = standard_prover("agent:claude", backend=DockerBackend())
task = example_task(EXAMPLE.MUL_REORDER)

result = prover.prove(task, tempfile.mkdtemp())
print(result.success)
```

## Available provers

Each name is accepted by the `--provers` CLI flag and the prover registry. The
agentic provers run a coding-agent *harness* (staged into the sandbox) sharing
[lean-lsp-mcp](https://github.com/oOo0oOo/lean-lsp-mcp); the shared `Verifier`
does the final check regardless of which tool generated the proof.

| Prover | Backing tool | Source / website |
| --- | --- | --- |
| `aristotle` | Harmonic Aristotle (hosted) | [harmonic.fun](https://www.harmonic.fun) · [aristotlelib](https://pypi.org/project/aristotlelib/) |
| `agent` | Claude Code (default) | [anthropics/claude-code](https://github.com/anthropics/claude-code) |
| `codex` | OpenAI Codex CLI | [openai/codex](https://github.com/openai/codex) |
| `opencode` | opencode | [sst/opencode](https://github.com/sst/opencode) |
| `axprover` | ax-prover (LangGraph Lean agent) | [Axiomatic-AI/ax-prover-base](https://github.com/Axiomatic-AI/ax-prover-base) ([fork](https://github.com/henryrobbins/ax-prover-base)) |
| `numina` | Numina skills/prompts on Claude Code | [vendor/numina/VENDOR.md](vendor/numina/VENDOR.md) |
| `vibe` | Mistral Vibe `lean` scaffold | [mistralai/mistral-vibe](https://github.com/mistralai/mistral-vibe) |

Both `DockerBackend` and `ModalBackend` run the provers and the shared
`Verifier` end-to-end against the Mathlib image; pick one with `--backend`, or
split generation from the cheap verify with `--agent-backend`.

## Development

See `AGENTS.md` for development information.

## License

[MIT](LICENSE)
