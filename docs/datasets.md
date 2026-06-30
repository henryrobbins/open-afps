# Datasets

OpenATP provides utilities to download common proof-synthesis benchmarks (see {ref}`downloading-a-dataset`). The available datasets are listed in the {class}`~open_atp.benchmark.DATASET` enum. We list each in the table below.

| Benchmark | `DATASET` | Toolchain | Paper | Source |
| --- | --- | --- | --- | --- |
| {doc}`/examples` | `EXAMPLES` | `v4.28.0` | — | {doc}`API </api/examples>` |
| PutnamBench | `PUTNAM` | `v4.27.0` | {cite:t}`tsoukalas2024putnambench` | [GitHub](https://github.com/trishullab/PutnamBench) |
| FATE-H | `FATE_H` | `v4.28.0` | {cite:t}`jiang2025fate` | [GitHub](https://github.com/frenzymath/FATE-H) |
| FATE-M | `FATE_M` | `v4.28.0` | {cite:t}`jiang2025fate` | [GitHub](https://github.com/frenzymath/FATE-M) |
| FATE-X | `FATE_X` | `v4.28.0` | {cite:t}`jiang2025fate` | [GitHub](https://github.com/frenzymath/FATE-X) |

:::{warning}
PutnamBench pins an older version of Lean than the default image. A custom skeleton must be supplied to {func}`~open_atp.benchmark.tasks_from_dir` and the Docker image must be rebuilt with version `v4.27.0` of Lean and Mathlib as well.
:::
