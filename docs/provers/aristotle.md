(prover-aristotle)=
# AristotleProver

```{include} _meta_aristotle.md
:parser: myst
```

The {class}`~open_atp.provers.aristotle.AristotleProver` wraps Harmonic's hosted
[Aristotle](https://www.harmonic.fun/) API. No agentic sandbox is needed for
generation — the lake project is handed to the hosted agent via `aristotlelib`
(submit → wait → download), the returned archive is unpacked over the workdir, and
the shared {class}`~open_atp.verify.Verifier` does the final check in a local
Docker sandbox. This is the platform's simplest end-to-end slice.

## Authentication

The prover reads the Harmonic API key from the `ARISTOTLE_API_KEY` environment
variable (or pass it explicitly as
{attr}`~open_atp.provers.aristotle.AristotleProver` `api_key`). Set it on the host:

```bash
export ARISTOTLE_API_KEY=...
```

or add it to a `.env` file in your project.

## Usage

```python
from open_atp.backends.docker import DockerBackend
from open_atp.images import DEFAULT_IMAGE
from open_atp.provers.aristotle import AristotleProver

backend = DockerBackend(image=DEFAULT_IMAGE)
prover = AristotleProver(backend=backend)
```

The remote interaction is isolated in
`AristotleProver._submit_and_download`, so tests can stand in a fake result without
touching the network or an API key. See {doc}`../user_guide/run_provers` for an
end-to-end run and {class}`~open_atp.provers.aristotle.AristotleProver` in the
{doc}`../api/provers` reference for configuration.

The prompt submitted to the hosted agent is Aristotle's own prover prompt, with the
task's optional `user_prompt` appended under an *Additional instructions* heading
when set (the agent CLI harnesses share a longer, tool-specific prover prompt
instead):

:::{dropdown} Aristotle prover prompt
:icon: code
```{literalinclude} ../../src/open_atp/provers/aristotle.py
:language: python
:start-after: PROVER_PROMPT = (
:end-before: END PROVER_PROMPT
```
:::

:::{note}
Aristotle runs are billed by Harmonic against your `ARISTOTLE_API_KEY`. Verification
still happens locally in your own Docker sandbox.
:::
