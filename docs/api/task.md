# `core.task`

The input contract: the Lean project to complete and the task describing what to
fill. A project is a *full lake project* carrying its own `lean-toolchain` and
`lake-manifest.json`.

```{eval-rst}
.. autoclass:: open_afps.core.task.LeanProject

.. autoclass:: open_afps.core.task.ProofTask

.. autoexception:: open_afps.core.task.ToolchainMismatch
   :no-members:
```

## Image defaults

The constants describing the baked sandbox image (the contract the verifier
enforces).

```{eval-rst}
.. autodata:: open_afps.images.DEFAULT_IMAGE

.. autodata:: open_afps.images.DEFAULT_TOOLCHAIN

.. autodata:: open_afps.images.DEFAULT_MATHLIB_REV
```
