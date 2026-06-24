"""Small input-staging helpers for the *"upload"* contract.

A full lake project on disk is already a :class:`~open_afps.core.task.LeanProject`
(just ``LeanProject(Path(path))``); the only nontrivial case is staging one or more
bare ``.lean`` files into the pinned Mathlib skeleton, which :func:`stage_files` does.
"""

from __future__ import annotations

import shutil
from collections.abc import Sequence
from pathlib import Path

from open_afps.core.task import LeanProject
from open_afps.images import SKELETON_DIR


def stage_files(
    files: Sequence[Path | str],
    dest: Path | str,
    *,
    skeleton: Path = SKELETON_DIR,
) -> LeanProject:
    """Stage bare ``.lean`` files into the default Mathlib skeleton -> a project.

    Convenience for the *"upload one or more ``.lean`` files"* contract: copies the
    skeleton's ``lakefile.toml`` + ``lean-toolchain`` into ``dest`` and drops the
    files at its root. Limitation: this only works for the pinned toolchain/deps the
    skeleton (and the baked image) provide -- a file needing a different Mathlib
    revision or extra deps must arrive as a full lake project instead.
    """
    if not (skeleton / "lean-toolchain").is_file():
        raise FileNotFoundError(
            f"No skeleton project at {skeleton} (only available in a source "
            "checkout); submit a full lake project directory instead."
        )
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    skeleton_files = (
        "lakefile.toml",
        "lakefile.lean",
        "lean-toolchain",
        "lake-manifest.json",
    )
    for name in skeleton_files:
        src = skeleton / name
        if src.is_file():
            shutil.copy2(src, dest / name)
    for f in files:
        f = Path(f)
        if f.suffix != ".lean":
            raise ValueError(f"Expected a .lean file, got {f}")
        shutil.copy2(f, dest / f.name)
    return LeanProject(dest)
