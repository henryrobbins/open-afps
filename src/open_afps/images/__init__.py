"""Defaults for the baked sandbox image.

These describe the image built from ``images/Dockerfile`` and are the contract the
verifier enforces: an uploaded project must pin :data:`DEFAULT_TOOLCHAIN`.
"""

#: Tag produced by ``docker build -t open-afps:latest images/``.
DEFAULT_IMAGE = "open-afps:latest"

#: Lean toolchain baked into ``DEFAULT_IMAGE`` (see ``images/lean/lean-toolchain``).
DEFAULT_TOOLCHAIN = "leanprover/lean4:v4.28.0"

#: Mathlib git tag whose olean cache is pre-baked (see ``images/lean/lakefile.toml``).
DEFAULT_MATHLIB_REV = "v4.28.0"

__all__ = ["DEFAULT_IMAGE", "DEFAULT_TOOLCHAIN", "DEFAULT_MATHLIB_REV"]
