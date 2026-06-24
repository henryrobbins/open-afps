---
tocdepth: 3
---

# `provers`

The concrete provers. Each subclasses {class}`~open_afps.provers.base.AutomatedProver`
and funnels its output through the shared {class}`~open_afps.core.verifier.Verifier`.
The agentic provers compose an {doc}`agent harness <harness>` (the *agent* concern)
with a {class}`~open_afps.backends.base.ComputeBackend` (the *compute* concern).

## Base

The base prover abstraction. An {class}`~open_afps.provers.base.AutomatedProver` is a
candidate generator; the base class owns the shared lifecycle (the public `prove`:
generate, then verify in the sandbox) so subclasses only implement `_generate`.

```{eval-rst}
.. autoclass:: open_afps.provers.base.AutomatedProver
   :exclude-members: name

.. autoclass:: open_afps.provers.base.AutomatedProverConfig
   :no-members:
```

## AgentProver

```{eval-rst}
.. autoclass:: open_afps.provers.agent_prover.AgentProver
   :show-inheritance:
   :exclude-members: name

.. autoclass:: open_afps.provers.agent_prover.AgentProverConfig
   :show-inheritance:
   :no-members:
```

## NuminaProver

```{eval-rst}
.. autoclass:: open_afps.provers.numina.NuminaProver
   :show-inheritance:
   :exclude-members: name

.. autoclass:: open_afps.provers.numina.NuminaProverConfig
   :show-inheritance:
   :no-members:
```

## AristotleProver

```{eval-rst}
.. autoclass:: open_afps.provers.aristotle.AristotleProver
   :show-inheritance:
   :exclude-members: name

.. autoclass:: open_afps.provers.aristotle.AristotleProverConfig
   :show-inheritance:
   :no-members:
```
