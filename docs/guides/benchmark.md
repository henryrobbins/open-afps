# Benchmarking Provers

A benchmark runs a set of provers across a set of proof tasks. This guide covers the dataset format, how to download datasets, and how to run a benchmark with both the Python API and the CLI.

## Prerequisites

- A compute backend configured: {doc}`Docker </guides/docker>` or
  {doc}`Modal </guides/modal>`.
- Credentials for whichever provers you run (see {doc}`/provers/index`).

## Dataset

A benchmark is just a directory of Lean tasks. OpenATP bundles several public proof-synthesis benchmarks (see {doc}`/datasets`). You can also create your own benchmarking datasets.

### Dataset structure

A dataset is a directory containing proof tasks in one of three styles:

- A single `.lean` file.
- A subdirectory containing multiple `.lean` files (considered a single task).
- A complete lake project (contains `lean-toolchain`, `lakefile.toml`, and `lake-manifest.json`).

A single dataset can contain a mix of these styles. The name of the task is derived from the file or subdirectory name. The example dataset below contains four tasks: `single_1`, `single_2`, `multi_file`, and `full_project`.

```
benchmark/
├── single_1.lean                # single file → task "single_1"
├── single_2.lean                # single file → task "single_2"
├── multi_file/                  # multiple files → task "multi_file"
│   ├── Defs.lean
│   └── Problem.lean
└── full_project/                # complete lake project → task "full_project"
    ├── lean-toolchain
    ├── lakefile.toml
    ├── lake-manifest.json
    └── FullProject/
        └── Problem.lean
```

### Loading a dataset

Datasets are loaded with {func}`~open_atp.benchmark.tasks_from_dir`, which returns a mapping of task names to {class}`~open_atp.lean.ProofTask` objects. We can load the example dataset above with:

```python
from open_atp.benchmark import tasks_from_dir

tasks = tasks_from_dir("benchmark")
list(tasks.keys())
>>> ['single_1', 'single_2', 'multi_file', 'full_project']
```

:::{warning}
Single and multi-file tasks are loaded with {meth}`~open_atp.lean.create_project` which uses a lake project skeleton pinned to `v4.28.0` of the Lean toolchain and Mathlib by default. If the dataset requires different versions, supply the `skeleton` argument to {func}`~open_atp.benchmark.tasks_from_dir` which forwards to {meth}`~open_atp.lean.create_project`.
:::

### Downloading a dataset

Common proof-synthesis benchmarks can be downloaded with {func}`~open_atp.benchmark.download_dataset`. The available datasets are listed in {doc}`/datasets`. The following example downloads the FATE-M {cite:p}`jiang2025fate` dataset into `datasets/fate-m`:

```python
from open_atp.benchmark import DATASET, download_dataset

src = download_dataset(DATASET.FATE_M, "datasets")
```

You can also use the CLI:

```bash
open-atp download fate-m datasets
```

The FATE-M dataset is a flat directory of single `.lean` files.

```
datasets/fate-m
├── 1.lean
├── 2.lean
├── 3.lean
├── ...
└── 100.lean
```

## Benchmark with the Python API

Use {func}`~open_atp.benchmark.run_benchmark` to run a set of provers across a set of tasks. It takes a mapping of task names to {class}`~open_atp.lean.ProofTask` objects, a mapping of prover names to {class}`~open_atp.provers.base.AutomatedProver` objects, and an output directory.

This example runs the Claude Code, Codex, and OpenCode provers across the FATE-M dataset.

```python
from pathlib import Path

from open_atp.backends.docker import DockerBackend
from open_atp.benchmark import DATASET, download_dataset, run_benchmark, tasks_from_dir
from open_atp.config import standard_prover

# Download the FATE-M dataset and load the tasks
src = download_dataset(DATASET.FATE_M, "datasets")
tasks = tasks_from_dir("datasets/fate-m")

# Define the provers to benchmark
backend = DockerBackend()
provers = {
    name: standard_prover(name, backend=backend)
    for name in ("agent:claude", "agent:codex", "agent:opencode")
}

# Run the benchmark
result = run_benchmark(tasks, provers, Path("runs/fate-m"))
```

The returned {class}`~open_atp.benchmark.BenchmarkResult` collects a list of {class}`~open_atp.benchmark.BenchmarkRun` objects which combine each (task, prover) pair with its {class}`~open_atp.provers.base.ProofResult`. The output directory contains a subdirectory `<task>/<prover>` for each pair with the same structure as a single run (see {ref}`prover-output`).

Use `only` to restrict to a subset of the tasks and `max_workers` to control concurrency. See the {doc}`/api/index` for the full signature of {func}`~open_atp.benchmark.run_benchmark`.

```python
result = run_benchmark(
    tasks, provers, Path("runs/fate-m"),
    only=["1", "2", "3"],
    max_workers=10,
)
```

## Benchmark with the CLI

The `open-atp benchmark` command is a thin shell over the same API. Provide a path to the dataset, an output destination for the result, and optionally a list of provers to run.

### Benchmark standard provers

We can reproduce the above Python API example with the following CLI command. We provide a list of standard provers to `--provers`, set the compute backend to Docker with `--compute`, restrict to the first three tasks with `--tasks`, and finally set `--workers` to 10 to allow up to 10 concurrent runs.

```console
$ open-atp benchmark datasets/fate-m runs/fate-m \
    --provers agent:claude,agent:codex,agent:opencode \
    --compute docker \
    --tasks 1,2,3 \
    --workers 10
╭──────┬───────────────────┬────────┬─────────┬──────╮
│ task │ prover            │ status │    cost │ time │
├──────┼───────────────────┼────────┼─────────┼──────┤
│ 1    │ agent:claude_code │   ✓    │ $0.4703 │ 150s │
│ 1    │ agent:codex       │   ✓    │ $0.6480 │ 140s │
│ 1    │ agent:opencode    │   ✓    │ $0.2257 │ 129s │
│ 2    │ agent:claude_code │   ✓    │ $0.5292 │ 141s │
│ 2    │ agent:codex       │   ✓    │ $0.7480 │ 139s │
│ 2    │ agent:opencode    │   ✓    │ $0.1336 │ 135s │
│ 3    │ agent:claude_code │   ✓    │ $0.2901 │ 153s │
│ 3    │ agent:codex       │   ✓    │ $0.4865 │ 147s │
│ 3    │ agent:opencode    │   ✓    │ $0.2048 │ 139s │
╰──────┴───────────────────┴────────┴─────────┴──────╯
```

### Using a YAML config

It is often useful to configure a benchmark with a YAML file. The YAML configuration supports the same keys as the CLI flags: `provers`, `tasks`, `compute`, and `workers`. The `provers` key accepts a list of standard prover names *or* a custom prover configuration can be supplied. The below example uses the OpenCode standard prover and two custom agent provers that override the default model and effort level.

```yaml
# config.yaml
compute: docker
workers: 10
tasks: [1, 2, 3]
provers:
  - type: agent
    harness:
      type: claude_code
      model: claude-opus-4-8
      effort: medium
  - type: agent
    harness:
      type: codex
      model: gpt-5.5
      effort: medium
  - agent:opencode
```

Supply the config to the benchmark with `--config`:

```bash
open-atp benchmark datasets/fate-m runs/fate-m --config config.yaml
```

The YAML configuration can be overridden by CLI flags.

```bash
open-atp benchmark datasets/fate-m runs/fate-m --config config.yaml --compute modal
```

See {doc}`/cli` for the full reference.
