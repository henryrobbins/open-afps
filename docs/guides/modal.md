# Running Remotely with Modal

`open-atp` can run commands in [Modal](https://modal.com/) Sandboxes instead of
local Docker containers. Each run gets its own cloud Sandbox, which avoids duplicate
[Lean](https://lean-lang.org/) environments and lets many runs proceed in parallel
without consuming local resources.

## Install Modal

Modal ships as a dependency of `open-atp`. You'll need a Modal account — sign up at
[modal.com](https://modal.com/signup) if you don't have one. Then authenticate the
`modal` CLI against your Modal workspace (this writes a token to `~/.modal.toml`):

```bash
modal setup
```

Verify the credentials are working with:

```bash
modal app list
```

## Build the Modal image

Unlike Docker, Modal Sandboxes have an isolated filesystem and ignore a container
`USER`, so the sandbox image is built and published programmatically (rather than
from `images/Dockerfile`). It installs the Lean toolchain and agent CLIs globally as
root and bakes the same warm Mathlib `olean` cache. Build and publish it with:

```bash
open-atp build-modal-image
```

This publishes a named Modal image (`open-atp` by default) that the backend looks
up at run time. The name must match `ModalBackend`'s `image` (sans `:tag`); pass `--name`
to publish under a different name and `--force` to rebuild even when Modal has cached
layers. As with Docker, the first build pre-builds Mathlib and is expected to take a
while.

## Testing Modal

A {class}`~open_atp.backends.modal.ModalBackend` is a drop-in
{class}`~open_atp.backends.base.ComputeBackend` — substitute it for the
`DockerBackend` anywhere a compute backend is expected. To confirm the published
image is wired up correctly, prove one of the bundled
{doc}`example formulations <../examples>` with the `agent:claude` prover against a
`ModalBackend`. This exercises the whole pipeline (stage → generate → verify) end to
end:

```python
from open_atp import standard_prover
from open_atp.backends.modal import ModalBackend
from open_atp.examples import EXAMPLE, example_task

prover = standard_prover("agent:claude", backend=ModalBackend(cpu=4.0, memory_mib=4096))
result = prover.prove(example_task(EXAMPLE.MUL_REORDER), "runs/modal_test")
print("success:", result.success)
```

`cpu` is a guaranteed floor of cores (the Sandbox may burst higher) and `memory_mib`
is in MiB. See the {doc}`/api/backends` reference for the full set of options. This
also needs a Claude Code credential (see {doc}`../provers/claude_code`).

:::{note}
Running on Modal incurs cloud compute charges billed by your Modal workspace. See
[Modal's pricing](https://modal.com/pricing) for details.
:::
