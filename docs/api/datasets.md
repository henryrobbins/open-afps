# `datasets`

Download the public Lean benchmark datasets as directories of `.lean` task files. Each
known dataset lives in a subdirectory of a GitHub repo —
[PutnamBench](https://github.com/trishullab/PutnamBench)'s `lean4/src`,
[FATE](https://github.com/frenzymath/FATE)'s `FATE{H,M,X}`.
{func}`~open_atp.datasets.download_dataset` fetches just that subdirectory (a shallow,
blobless, sparse clone) and returns the local path, ready for
{func}`~open_atp.benchmark.tasks_from_dir`.

## Download

```{eval-rst}
.. autofunction:: open_atp.datasets.download_dataset
```

## Catalog

```{eval-rst}
.. autodata:: open_atp.datasets.DATASETS

.. autoclass:: open_atp.datasets.Dataset
```
