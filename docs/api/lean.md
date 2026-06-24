# `lean`

The Lean input contract: the project to complete, the task describing what to fill,
and the staging helper. A project is a *full lake project* carrying its own
`lean-toolchain` and `lake-manifest.json`.

```{eval-rst}
.. autoclass:: open_atp.lean.LeanProject
   :exclude-members: root, lean_toolchain, mathlib_rev

.. autoclass:: open_atp.lean.ProofTask
   :exclude-members: project, targets, instructions, metadata

.. autoexception:: open_atp.lean.ToolchainMismatch
   :no-members:

.. autofunction:: open_atp.lean.stage_files
```

## Staging input

A full lake project on disk is just `LeanProject(Path(path))`.
{func}`~open_atp.lean.stage_files` stages one or more bare `.lean` files into the
pinned Mathlib skeleton.

## Image defaults

The constants describing the baked sandbox image (the contract the verifier
enforces).

```{eval-rst}
.. autodata:: open_atp.images.DEFAULT_IMAGE

.. autoclass:: open_atp.images.Image
   :members:
```
