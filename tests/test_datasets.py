"""Dataset download tests (no network).

The git clone is the one side effect, so these stub
:func:`subprocess.run`: an unknown name is rejected, a known dataset issues the
sparse-clone + ``sparse-checkout set`` for the right subdir, and an already-present
download is reused without cloning.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from open_atp import datasets
from open_atp.datasets import DATASETS, download_dataset


def test_unknown_dataset_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="unknown dataset"):
        download_dataset("nope", tmp_path)


def test_sparse_clones_the_subdir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[list[str]] = []

    def fake_run(cmd: list[str], **_: object) -> subprocess.CompletedProcess[bytes]:
        calls.append(cmd)
        if "clone" in cmd:  # emulate the clone materializing repo + subdir
            (Path(cmd[-1]) / DATASETS["putnam"].subdir).mkdir(parents=True)
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(datasets.subprocess, "run", fake_run)

    path = download_dataset("putnam", tmp_path)

    assert path == tmp_path / "putnam" / "lean4" / "src"
    clone = next(c for c in calls if "clone" in c)
    assert "--sparse" in clone and "--depth" in clone
    assert clone[-2] == "https://github.com/trishullab/PutnamBench.git"
    set_cmd = next(c for c in calls if "sparse-checkout" in c)
    assert set_cmd[-1] == "lean4/src"


def test_existing_download_is_reused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "fate-m" / "FATEM").mkdir(parents=True)

    def boom(*_: object, **__: object) -> object:
        raise AssertionError("should not clone a cached dataset")

    monkeypatch.setattr(datasets.subprocess, "run", boom)

    assert download_dataset("fate-m", tmp_path) == tmp_path / "fate-m" / "FATEM"
