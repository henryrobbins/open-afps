# `api`

The `open_afps.api` module is the prover registry: it maps a prover name to a
constructed {class}`~open_afps.provers.base.AutomatedProver`, wired to a shared
sandbox image/toolchain and compute backend. A caller then drives the prover directly
via {meth}`~open_afps.provers.base.AutomatedProver.prove`, which returns a
{class}`~open_afps.core.result.ProofResult` with verification and cost.

This is the top-level surface re-exported from `open_afps` itself.

## Provers

{class}`~open_afps.api.PROVERS` enumerates the available provers (e.g.
`PROVERS.CLAUDE`, `PROVERS.CODEX`, `PROVERS.ARISTOTLE`).
{func}`~open_afps.api.get_prover` maps a member (or its string value) to a constructed
{class}`~open_afps.provers.base.AutomatedProver`, wiring in the shared image/toolchain,
the verify backend, and (for agentic provers) the agent backend.

```{eval-rst}
.. autoclass:: open_afps.api.PROVERS
   :members:

.. autofunction:: open_afps.api.get_prover

.. autofunction:: open_afps.api.available_provers

.. autofunction:: open_afps.api.make_backend
```

## Staging input

A full lake project on disk is just `LeanProject(Path(path))`.
{func}`~open_afps.utils.stage_files` stages one or more bare `.lean` files into the
pinned Mathlib skeleton.

```{eval-rst}
.. autofunction:: open_afps.utils.stage_files
```
