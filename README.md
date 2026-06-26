<p align="center">
  <img src="docs/_static/logo_light.svg" alt="OpenATP" width="420">
</p>

[![PyPI](https://img.shields.io/pypi/v/open-atp.svg)](https://pypi.org/project/open-atp/)
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

The `ID` is the `standard_prover` catalog name; the `--provers` CLI flag also
accepts the short prover names (`agent`, `codex`, `aristotle`, ...). The agentic
provers run a coding-agent *harness* (staged into the sandbox) sharing
[lean-lsp-mcp](https://github.com/oOo0oOo/lean-lsp-mcp); the shared `Verifier`
does the final check regardless of which tool generated the proof.

<!-- BEGIN PROVER TABLE (generated from docs/provers.yaml) -->
| Prover | ID | Skills | MCP | Paper | Source |
| --- | --- | --- | --- | --- | --- |
| [Claude Code](docs/provers/claude_code.md) | `agent:claude` | [leanprover](https://github.com/leanprover/skills), [lean4](https://github.com/cameronfreer/lean4-skills) | ✓ | — | — |
| [Codex](docs/provers/codex.md) | `agent:codex` | [leanprover](https://github.com/leanprover/skills) | ✓ | — | [GitHub](https://github.com/openai/codex) |
| [OpenCode](docs/provers/opencode.md) | `agent:opencode` | [leanprover](https://github.com/leanprover/skills) | ✓ | — | [GitHub](https://github.com/sst/opencode) |
| [AxProver](docs/provers/axprover.md) | `agent:axprover` | — | ✗ | [Requena et al. 2026](https://openreview.net/forum?id=E30g7bO7rU) | [GitHub](https://github.com/Axiomatic-AI/ax-prover-base) |
| [Vibe / Leanstral](docs/provers/vibe.md) | `agent:vibe` | [leanprover](https://github.com/leanprover/skills) | ✓ | [Leanstral (blog)](https://mistral.ai/news/leanstral) | [HuggingFace](https://huggingface.co/mistralai/Leanstral-2603) |
| [NuminaProver](docs/provers/numina.md) | `numina` | — | ✓ | [Liu et al. 2026](https://arxiv.org/abs/2601.14027) | [GitHub](https://github.com/project-numina/numina-lean-agent) |
| [AristotleProver](docs/provers/aristotle.md) | `aristotle` | — | ✗ | [Achim et al. 2025](https://arxiv.org/abs/2510.01346) | — |
<!-- END PROVER TABLE -->

Both `DockerBackend` and `ModalBackend` run the provers and the shared
`Verifier` end-to-end against the Mathlib image; pick one with `--backend`, or
split generation from the cheap verify with `--agent-backend`.

## Citing

If you use `OpenATP` in your work, please cite it:

```bibtex
@software{openatp,
  title = {OpenATP: Open Automated Theorem Proving},
  author = {Henry Robbins},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/henryrobbins/open-atp}
}
```

Several of the bundled provers have associated papers — see the
[provers documentation](https://open-atp.readthedocs.io/en/latest/provers/)
for the methods to cite when you use them.

## Development

See `AGENTS.md` for development information.

## License

[MIT](LICENSE)
