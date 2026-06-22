# Installation

## Install the package

`open-afps` targets Python 3.12+. Install it from source with
[uv](https://docs.astral.sh/uv/) (recommended for development):

```bash
git clone https://github.com/henryrobbins/open-afps.git
cd open-afps
uv sync
```

or with `pip`:

```bash
pip install open-afps
```

## Quickstart

This quickstart compiles and checks a complete lake project in a local Docker
sandbox via the shared {class}`~open_afps.core.verifier.Verifier`. It requires:

- **Docker** installed and the `open-afps:latest` image built (see
  {doc}`user_guide/docker`).
- A **complete lake project** — a directory carrying its own `lean-toolchain` and
  `lake-manifest.json` — whose toolchain matches the image's pin
  ({data}`~open_afps.images.DEFAULT_TOOLCHAIN`).

```python
from open_afps.core.task import LeanProject
from open_afps.core.verifier import docker_verifier

report = docker_verifier().verify(LeanProject("path/to/lake/project"))
print(report.verified, report.sorry_free, report.axioms)
```

To go further than verification and actually *fill* the `sorry`s, hand a project to
a prover. See {doc}`provers/index` for the prover catalogue and
{doc}`user_guide/run_provers` for an end-to-end walkthrough.

:::{note}
The input contract is a **full lake project**. The verifier rejects projects whose
pinned toolchain does not match the sandbox image
({class}`~open_afps.core.task.ToolchainMismatch`) rather than failing deep in a
build.
:::
