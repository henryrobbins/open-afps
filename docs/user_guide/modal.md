# Modal

`open-afps` can run commands in [Modal](https://modal.com/) Sandboxes instead of
local Docker containers. Each run gets its own cloud Sandbox, which avoids duplicate
[Lean](https://lean-lang.org/) environments and lets many runs proceed in parallel
without consuming local resources.

:::{warning}
The {class}`~open_afps.backends.modal.ModalBackend` is currently a **skeleton**:
{meth}`~open_afps.backends.modal.ModalBackend.start` raises `NotImplementedError`.
The interface below is stable, but the implementation is still being ported from the
Docker backend. Use {doc}`docker` for now.
:::

## Install Modal

Modal ships as a dependency of `open-afps`. Authenticate the `modal` CLI against your
Modal workspace (this writes a token to `~/.modal.toml`):

```bash
modal setup
```

Verify the credentials are working with:

```bash
modal app list
```

## Using the Modal backend

A {class}`~open_afps.backends.modal.ModalBackend` is constructed from a
{class}`~open_afps.backends.modal.ModalConfig` and is a drop-in
{class}`~open_afps.backends.base.ComputeBackend` — substitute it for the
`DockerBackend` anywhere a verification or generation backend is expected:

```python
from open_afps.backends.modal import ModalBackend, ModalConfig
from open_afps.images import DEFAULT_IMAGE

backend = ModalBackend(ModalConfig(image=DEFAULT_IMAGE, cpu=4.0, memory_mib=4096))
```

`cpu` is a guaranteed floor of cores (the Sandbox may burst higher) and `memory_mib`
is in MiB. See the {doc}`/api/backends` reference for the full set of options.

:::{note}
Running on Modal incurs cloud compute charges billed by your Modal workspace. See
[Modal's pricing](https://modal.com/pricing) for details.
:::
