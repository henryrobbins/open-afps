# `core.task`

The input contract: the Lean project to complete and the task describing what to
fill. A project is a *full lake project* carrying its own `lean-toolchain` and
`lake-manifest.json`.

```{eval-rst}
.. autoclass:: open_atp.core.task.LeanProject

.. autoclass:: open_atp.core.task.ProofTask

.. autoexception:: open_atp.core.task.ToolchainMismatch
   :no-members:
```

## Image defaults

The constants describing the baked sandbox image (the contract the verifier
enforces).

```{eval-rst}
.. autodata:: open_atp.images.DEFAULT_IMAGE

.. autodata:: open_atp.images.DEFAULT_TOOLCHAIN

.. autodata:: open_atp.images.DEFAULT_MATHLIB_REV
```
