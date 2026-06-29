# Running Remotely with Modal

OpenATP supports running agentic provers remotely in [Modal](https://modal.com/) Sandboxes. Modal bills for compute per second -- see current [pricing](https://modal.com/pricing). In this guide, we will authenticate with the Modal CLI, build the OpenATP Modal image, and test everything by verifying a small theorem.

## Authenticate with the Modal CLI

First, create a [Modal account](https://modal.com/signup) if you don't have one. The `open-atp` Python package ships with the `modal` dependency. Authenticate using the `modal` CLI (this writes a token to `~/.modal.toml`):

```bash
modal setup
```

## Build the Modal image

Modal Sandbox containers are created from the same OpenATP default Docker image. Before running any prover, you must create the image on Modal. Build it with the `open-atp` CLI:

```bash
open-atp build-modal-image
```

Use the Modal CLI to check the image was created successfully.

```bash
$ modal image names list
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ Tag                ┃ Image ID                  ┃ Updated at           ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│ open-atp:latest    │ im-9rcKV2cJKID4nhE4GQGbPm │ 2026-06-25 17:39 EDT │
└────────────────────┴───────────────────────────┴──────────────────────┘
```

The Docker image for Modal is nearly identical to the `Dockerfile` used to build the local Docker image. It is built programmatically using the `modal` Python package for more effective caching.

:::{dropdown} `_build_modal_image()`
:icon: code
```{literalinclude} ../../src/open_atp/__main__.py
:language: python
:pyobject: _build_modal_image
```
:::

## Test the image

To confirm the image was built correctly, use the test method below. It verifies a trivial proof inside the Modal Sandbox container. No prover is run and no agent credentials are needed.

```python
from open_atp.backends.modal import ModalBackend

assert ModalBackend().test()
```

## Configure and monitor resources

{class}`~open_atp.backends.modal.ModalBackend` accepts `cpu` (a guaranteed floor of cores; the Sandbox may burst higher) and `memory_mib` (in MiB). It is recommended to budget at least 2 CPUs and 4 GB of memory. This was found to achieve a good time/cost tradeoff.

```python
from open_atp.backends.modal import ModalBackend

backend = ModalBackend(cpu=2.0, memory_mib=4096)
```

Live Sandboxes, their resource usage, and per-second cost are visible from the
[Modal dashboard](https://modal.com/apps). You can also terminate runaway jobs from the dashboard.
