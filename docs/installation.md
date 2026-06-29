# Installation

## Install the package

Install `open-atp` from PyPI with `pip`:

```bash
pip install open-atp
```

## Quickstart

This quickstart runs the Claude Code agent harness in a local Docker container to prove a small example theorem (see {ref}`MUL_REORDER`). For a more detailed guide, see {doc}`/guides/run_provers`.

### Prerequisites

- Docker installed and the `open-atp:latest` image built (see
  {doc}`/guides/docker`).
- A `CLAUDE_CODE_OAUTH_TOKEN` in your environment (see {doc}`/provers/claude_code` authentication).

### Running the prover

```python
from pathlib import Path

from open_atp.backends.docker import DockerBackend
from open_atp.config import standard_prover
from open_atp.examples import EXAMPLE, example_task

task = example_task(EXAMPLE.MUL_REORDER)
prover = standard_prover("claude", backend=DockerBackend())
result = prover.prove(task, output_dir=Path("demo"))
```

### Inspecting the results

Generating this proof will take 2-3 minutes on the first run. The resulting files will be created.

```
demo
├── logs
│   ├── result.json
│   └── stdout.txt
└── wd
    ├── agent_prompt.txt
    ├── agent.sh
    ├── lake-manifest.json
    ├── lakefile.toml
    ├── lean-toolchain
    └── MulReorder.lean
```

The generated proof, likely a simple application of the `ring` tactic, can be found in the Lean file: `MulReorder.lean`.

```
import Mathlib

/-! From *Mathematics in Lean*, C02 "Calculating": reorder a product of reals
using commutativity and associativity. -/

example (a b c : ℝ) : c * b * a = b * (a * c) := by
  ring
```
