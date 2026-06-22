---
tocdepth: 3
---

# `backends`

A {class}`~open_afps.backends.base.ComputeBackend` runs a command over a working
directory inside a Lean+Mathlib sandbox. It is the single load-bearing primitive of
the platform, used both to run a coding agent and to run `lake env lean ...` for
verification.

## Base

```{eval-rst}
.. autoclass:: open_afps.backends.base.ComputeBackend
   :exclude-members: name

.. autoclass:: open_afps.backends.base.BackendConfig
   :no-members:

.. autoclass:: open_afps.backends.base.CommandHandle

.. autoclass:: open_afps.backends.base.CommandResult
   :no-members:
```

## Docker

```{eval-rst}
.. autoclass:: open_afps.backends.docker.DockerBackend
   :show-inheritance:
   :exclude-members: name, start

.. autoclass:: open_afps.backends.docker.DockerConfig
   :show-inheritance:
   :no-members:
```

## Modal

```{eval-rst}
.. autoclass:: open_afps.backends.modal.ModalBackend
   :show-inheritance:
   :exclude-members: name, start

.. autoclass:: open_afps.backends.modal.ModalConfig
   :show-inheritance:
   :no-members:
```
