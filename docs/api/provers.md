---
tocdepth: 3
---

# `provers`

The concrete provers. Each subclasses {class}`~open_afps.core.prover.AutomatedProver`
and funnels its output through the shared {class}`~open_afps.core.verifier.Verifier`.

## AgentProver

```{eval-rst}
.. autoclass:: open_afps.provers.agent.prover.AgentProver
   :show-inheritance:
   :exclude-members: name

.. autoclass:: open_afps.provers.agent.prover.AgentProverConfig
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

## KiminaProver

```{eval-rst}
.. autoclass:: open_afps.provers.kimina.KiminaProver
   :show-inheritance:
   :exclude-members: name

.. autoclass:: open_afps.provers.kimina.KiminaProverConfig
   :show-inheritance:
   :no-members:
```

### Splice helpers

```{eval-rst}
.. autofunction:: open_afps.provers._lean_splice.extract_theorems

.. autofunction:: open_afps.provers._lean_splice.splice_proof

.. autoclass:: open_afps.provers._lean_splice.Theorem
   :no-members:
```

(agent-harnesses)=
## Agent harnesses

A {class}`~open_afps.provers.agent.harness.Harness` is the *agent* concern of the
{class}`~open_afps.provers.agent.prover.AgentProver`: launch script, credential
forwarding, and output parsing for one agent CLI. See {doc}`../agent_harness/index`
for setup.

```{eval-rst}
.. autoclass:: open_afps.provers.agent.harness.Harness
   :exclude-members: name

.. autoclass:: open_afps.provers.agent.harness.HarnessRunResult
   :no-members:

.. autoclass:: open_afps.provers.agent.harness.AuthSpec
   :no-members:

.. autoclass:: open_afps.provers.agent.harness.ClaudeCodeHarness
   :show-inheritance:
   :exclude-members: configure_wd, name

.. autoclass:: open_afps.provers.agent.harness.CodexHarness
   :show-inheritance:
   :exclude-members: configure_wd, name

.. autoclass:: open_afps.provers.agent.harness.OpenCodeHarness
   :show-inheritance:
   :exclude-members: configure_wd, name

.. autodata:: open_afps.provers.agent.harness.HARNESSES
```

## Pricing

```{eval-rst}
.. autodata:: open_afps.provers.agent.cost.COST_PER_MTOK
```
