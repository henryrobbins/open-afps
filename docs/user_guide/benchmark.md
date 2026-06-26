# Benchmarking provers

To compare provers, {func}`~open_atp.benchmark.run_benchmark` runs every
`(task, prover)` pair and writes each cell to
`output_dir/<task>/<prover>/{wd,logs,results.json}`. Both tasks and provers are passed
as **name → object** mappings (the names become the subdirectory names, so several
provers sharing a class `name` — every `agent:*` is `"agent"` — stay distinct):

```python
from pathlib import Path

from open_atp.backends.docker import DockerBackend
from open_atp.benchmark import run_benchmark
from open_atp.config import standard_prover
from open_atp.examples import EXAMPLE, example_task
from open_atp.images import DEFAULT_IMAGE

backend = DockerBackend(image=DEFAULT_IMAGE)
tasks = {EXAMPLE.MUL_REORDER.value: example_task(EXAMPLE.MUL_REORDER)}
provers = {
    name: standard_prover(name, backend=backend)
    for name in ("agent:claude", "numina")
}

result = run_benchmark(tasks, provers, Path("runs/benchmark"))
print(result.table())
```

The returned {class}`~open_atp.benchmark.BenchmarkResult` collects every cell
(`result.runs`) and renders a terminal table with one row per `(task, prover)`. A
prover that raises is recorded as a failed
{class}`~open_atp.provers.base.ProofResult` (its `error` captured) so one bad run never
aborts the sweep.

The `open-atp ex-benchmark` CLI command runs exactly this sweep over all
{func}`~open_atp.config.standard_provers` and the five bundled
{class}`~open_atp.examples.EXAMPLE` tasks; pick the backend with
`--compute {docker,modal}`.

## Tasks from a directory

To benchmark a directory of `.lean` files (each a `sorry`'d task),
{func}`~open_atp.benchmark.tasks_from_dir` builds the `tasks` mapping: each loose
`.lean` file becomes a task named by its stem, and each subdirectory becomes one
multi-file task.

## Downloading a dataset

{func}`~open_atp.benchmark.download_dataset` fetches the public benchmarks
({class}`~open_atp.benchmark.DATASET`: PutnamBench, FATE) — a sparse clone of just the
task subdirectory — straight into a directory ready for
{func}`~open_atp.benchmark.tasks_from_dir`:

```python
from open_atp.benchmark import DATASET, download_dataset, run_benchmark, tasks_from_dir

src = download_dataset(DATASET.FATE_M, "datasets")  # datasets/fate-m/FATEM
result = run_benchmark(tasks_from_dir(src), provers, Path("runs/fate-m"))
```

PutnamBench pins an older Lean than the default skeleton, so stage it against a
matching skeleton (`tasks_from_dir(src, skeleton=...)`).
