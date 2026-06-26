"""Download the public Lean benchmark datasets as directories of ``.lean`` task files.

Each known dataset lives in a subdirectory of a GitHub repo -- PutnamBench's
``lean4/src``, FATE's ``FATE{H,M,X}``. :func:`download_dataset` fetches just that
subdirectory (a shallow, blobless, sparse clone) and returns the local path, ready to
hand to :func:`~open_atp.benchmark.tasks_from_dir`::

    from open_atp.benchmark import run_benchmark, tasks_from_dir
    from open_atp.datasets import download_dataset

    src = download_dataset("fate-m", "datasets")
    run_benchmark(tasks_from_dir(src), provers, "runs/fate-m")

Each :class:`Dataset` records the toolchain it pins; PutnamBench is on an older Lean
than the default skeleton, so stage it with a matching ``skeleton`` (see
:func:`~open_atp.benchmark.tasks_from_dir`).
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Dataset:
    """A downloadable benchmark: the repo and the subdir holding its ``.lean`` tasks.

    Attributes
    ----------
    repo : str
        The GitHub ``owner/name``, cloned over HTTPS.
    subdir : str
        Path within the repo to the directory of task ``.lean`` files.
    toolchain : str
        The Lean toolchain the dataset pins (e.g. ``leanprover/lean4:v4.28.0``), for
        reference when choosing a ``skeleton`` for
        :func:`~open_atp.benchmark.tasks_from_dir`.
    """

    repo: str
    subdir: str
    toolchain: str


#: The known benchmark datasets, keyed by friendly name (the
#: :func:`download_dataset` ``name``).
DATASETS: dict[str, Dataset] = {
    "putnam": Dataset(
        repo="trishullab/PutnamBench",
        subdir="lean4/src",
        toolchain="leanprover/lean4:v4.27.0",
    ),
    "fate-h": Dataset(
        repo="frenzymath/FATE-H", subdir="FATEH", toolchain="leanprover/lean4:v4.28.0"
    ),
    "fate-m": Dataset(
        repo="frenzymath/FATE-M", subdir="FATEM", toolchain="leanprover/lean4:v4.28.0"
    ),
    "fate-x": Dataset(
        repo="frenzymath/FATE-X", subdir="FATEX", toolchain="leanprover/lean4:v4.28.0"
    ),
}


def download_dataset(
    name: str,
    dest: Path | str,
    *,
    ref: str | None = None,
) -> Path:
    """Download a benchmark dataset's task directory under ``dest``.

    Sparse-clones only the dataset's :attr:`Dataset.subdir` (shallow + blobless) into
    ``dest/<name>`` and returns the path to that subdirectory. An already-present
    download is reused as-is (the clone is skipped), so repeated calls are cheap.

    Parameters
    ----------
    name : str
        A :data:`DATASETS` key (``"putnam"``, ``"fate-h"``, ``"fate-m"``,
        ``"fate-x"``).
    dest : pathlib.Path or str
        Directory to clone into; the repo lands at ``dest/<name>``. Created if missing.
    ref : str, optional
        Branch or tag to check out. Default ``None`` -- the repo's default branch.

    Returns
    -------
    pathlib.Path
        The dataset's task directory (``dest/<name>/<subdir>``), a directory of
        ``.lean`` files ready for :func:`~open_atp.benchmark.tasks_from_dir`.
    """
    if name not in DATASETS:
        raise ValueError(f"unknown dataset {name!r}; choose from {sorted(DATASETS)}")
    dataset = DATASETS[name]
    dest = Path(dest)
    repo_dir = dest / name
    task_dir = repo_dir / dataset.subdir
    if task_dir.is_dir():
        return task_dir

    dest.mkdir(parents=True, exist_ok=True)
    url = f"https://github.com/{dataset.repo}.git"
    clone = ["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse"]
    if ref is not None:
        clone += ["--branch", ref]
    clone += [url, str(repo_dir)]
    subprocess.run(clone, check=True)
    subprocess.run(
        ["git", "-C", str(repo_dir), "sparse-checkout", "set", dataset.subdir],
        check=True,
    )

    if not task_dir.is_dir():
        raise FileNotFoundError(
            f"{dataset.repo} has no {dataset.subdir!r} at ref {ref or 'default'}"
        )
    return task_dir
