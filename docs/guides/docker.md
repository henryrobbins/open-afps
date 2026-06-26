# Running Locally with Docker

`open-atp` uses Docker to isolate agent working directories and to provide a
[Lean](https://lean-lang.org/) + [Mathlib](https://leanprover-community.github.io/)
sandbox with a warm `olean` cache. The same image backs both *generation* (the agent
runs inside it) and *verification* (the shared verifier compiles candidate files
inside it).

## Install Docker

Install either [Docker Desktop](https://docs.docker.com/desktop/) (recommended) or
[Docker Engine](https://docs.docker.com/engine/). Both include the `docker` CLI.
Verify the daemon is running with:

```bash
docker images
```

## Build the base image

The image is built from the `Dockerfile` under `images/`. It pins the supported Lean
toolchain ({attr}`~open_atp.images.Image.lean_toolchain`) and pre-builds a Mathlib
`olean` cache, so the first build is expected to take a while.

```bash
docker build -t open-atp:latest images/
```

Run `docker images` to verify the `open-atp` image was created. The large size is
mostly attributable to the bundled Mathlib library.

```
$ docker images
REPOSITORY   TAG       IMAGE ID       CREATED         SIZE
open-atp    latest    8c164dafcbc3   26 hours ago    12GB
```

The image bakes a warm Mathlib `olean` cache at `/workspace/.lake`; the
{class}`~open_atp.backends.docker.DockerBackend` symlinks each workdir's `.lake` to
it so projects build against the cache instead of compiling Mathlib from scratch. See
the `Dockerfile` below.

:::{dropdown} `images/Dockerfile`
:icon: code
```{literalinclude} ../../images/Dockerfile
:language: docker
```
:::

## Testing Docker

To confirm the image is wired up correctly, prove one of the bundled
{doc}`example formulations <../examples>` with the `agent:claude` prover against a
{class}`~open_atp.backends.docker.DockerBackend`. This exercises the whole pipeline
(stage → generate → verify) end to end:

```python
from open_atp import standard_prover
from open_atp.backends.docker import DockerBackend
from open_atp.examples import EXAMPLE, example_task

prover = standard_prover("agent:claude", backend=DockerBackend())
result = prover.prove(example_task(EXAMPLE.MUL_REORDER), "runs/docker_test")
print("success:", result.success)
```

This needs a Claude Code credential (see {doc}`../provers/claude_code`). For the full
prover lifecycle and how to read the {class}`~open_atp.provers.base.ProofResult`, see
{doc}`run_provers`.

## Docker resources

Docker lets you configure resource allocation. To run multiple agents in parallel,
budget roughly ~2 CPUs and ~3GB memory per agent on top of the daemon's baseline.

:::{warning}
It is not recommended to allocate *all* of your machine's resources in any single
category.
:::
