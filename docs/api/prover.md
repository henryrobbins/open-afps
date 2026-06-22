# `core.prover`

The base prover abstraction. An {class}`~open_afps.core.prover.AutomatedProver` is a
candidate generator; the base class owns the shared lifecycle (generate, then verify
in the sandbox) so subclasses only implement `prove`.

```{eval-rst}
.. autoclass:: open_afps.core.prover.AutomatedProver
   :exclude-members: name

.. autoclass:: open_afps.core.prover.AutomatedProverConfig
   :no-members:
```
