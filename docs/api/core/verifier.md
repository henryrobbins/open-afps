# `core.verifier`

The shared verifier: compile a candidate project in a sandbox and judge whether it
compiles, is `sorry`-free, and is axiom-clean. Every prover funnels its output
through this.

```{eval-rst}
.. autofunction:: open_afps.core.verifier.docker_verifier

.. autoclass:: open_afps.core.verifier.Verifier
   :members: check_compatible, verify
```
