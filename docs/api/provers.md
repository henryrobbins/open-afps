---
tocdepth: 3
---

# `provers`

The concrete provers and the registry/factory over them. Each prover subclasses
{class}`~open_atp.provers.base.AutomatedProver` and funnels its output through the
shared {class}`~open_atp.verify.Verifier`. The agentic provers compose an
{doc}`agent harness <harness>` (the *agent* concern) with a
{class}`~open_atp.backends.base.ComputeBackend` (the *compute* concern).

## Registry

The `open_atp.provers` registry maps a prover name to a constructed
{class}`~open_atp.provers.base.AutomatedProver`, wired to a shared sandbox
image/toolchain and compute backend. A caller then drives the prover directly
via {meth}`~open_atp.provers.base.AutomatedProver.prove`, which returns a
{class}`~open_atp.provers.base.ProofResult` with verification and cost. This is the
top-level surface re-exported from `open_atp` itself.

{data}`~open_atp.provers.PROVER_TYPES` maps each available prover name to its class (e.g.
`"agent"`, `"codex"`, `"aristotle"`).
{func}`~open_atp.provers.get_prover` maps a name to a constructed
{class}`~open_atp.provers.base.AutomatedProver`, wiring in the shared image/toolchain and
compute backend (e.g. `get_prover("agent")`, `get_prover("codex")`). Agentic provers run
generation in a live session over that backend and verify in the same hot sandbox.

```{eval-rst}
.. autodata:: open_atp.provers.PROVER_TYPES

.. autofunction:: open_atp.provers.get_prover

.. autofunction:: open_atp.provers.available_provers
```

## Base

The base prover abstraction. An {class}`~open_atp.provers.base.AutomatedProver` is a
candidate generator; the base class owns the shared lifecycle (the public `prove`:
generate, then verify in the sandbox) so subclasses only implement `_generate`.

```{eval-rst}
.. autoclass:: open_atp.provers.base.AutomatedProver
   :exclude-members: name

.. autoclass:: open_atp.provers.base.ProofResult
   :exclude-members: prover, verification, output_dir, completed_files, cost_usd, duration_s, metadata, error, wd, logs_dir, success
```

## AgentProver

```{eval-rst}
.. autoclass:: open_atp.provers.agent_prover.AgentProver
   :show-inheritance:
   :exclude-members: name
```

`AgentProver`'s `harness` is a {class}`~open_atp.harness.Harness` — pick the
CLI and its knobs by composing one (e.g.
`AgentProver(harness=VibeHarness(max_turns=8), backend=...)`). The per-harness classes
are documented under {doc}`harness`.

## NuminaProver

```{eval-rst}
.. autoclass:: open_atp.provers.numina.NuminaProver
   :show-inheritance:
   :exclude-members: name
```

## AristotleProver

```{eval-rst}
.. autoclass:: open_atp.provers.aristotle.AristotleProver
   :show-inheritance:
   :exclude-members: name
```
