# Running Locally with Docker

OpenATP requires Docker for running agentic provers locally. This is the *only* way to reliably restrict an agent to a working directory. In this guide, we will install Docker, build the OpenATP Docker image, and test everything by verifying a small theorem.

## Install Docker

Install either [Docker Desktop](https://docs.docker.com/desktop/) (recommended) or
[Docker Engine](https://docs.docker.com/engine/). Both include the `docker` CLI.
Verify the daemon is running with:

```bash
docker images
```

:::{warning}
If the Docker daemon is not running, you will get `RuntimeError: failed to start docker session container: docker: Cannot connect to the Docker daemon at unix:///Users/me/.docker/run/docker.sock. Is the docker daemon running?`
:::

## Build the image

OpenATP ships with a default Docker image providing a [Lean](https://lean-lang.org/) + [Mathlib](https://mathlib-initiative.org/) sandbox. It also includes the agent harness CLIs. The image is used both for running provers and the post-run verification step.

Build the image with the following command:

```bash
open-atp build-docker-image
```

Run `docker images` to verify the `open-atp` image was created. The large size is mostly attributable to the bundled Mathlib library.

```
$ docker images
REPOSITORY   TAG       IMAGE ID       CREATED         SIZE
open-atp     latest    8c164dafcbc3   1 hour ago      12GB
```

The image is built from this `Dockerfile`.

:::{dropdown} `images/Dockerfile`
:icon: code
```{literalinclude} ../../images/Dockerfile
:language: docker
```
:::

## Test the image

To confirm the image was built correctly, use the test method below. It verifies a trivial proof inside the Docker container. No prover is run and no agent credentials are needed.

```python
from open_atp.backends.docker import DockerBackend

assert DockerBackend().test()
```

## Configure resources

Docker lets you configure resource allocation. To run multiple agents in parallel,
budget roughly 2 CPUs and 4 GB of memory per agent on top of the daemon's baseline. To remove the bottleneck of local compute, OpenATP natively supports remote compute with {doc}`Modal </guides/modal>`!

:::{warning}
It is not recommended to allocate *all* of your machine's resources in any single
category.
:::
