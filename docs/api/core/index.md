# `core`

The `open_atp.core` package holds the input/output contracts and the shared verifier
every prover builds on:

- {doc}`task` — the input contract (`LeanProject`, `ProofTask`).
- {doc}`result` — the output types (`VerificationReport`, `ProofResult`).
- {doc}`verifier` — the shared `Verifier` (the final compile / sorry / axiom check).

The `AutomatedProver` base class lives with the concrete provers in {doc}`../provers`.

```{toctree}
:maxdepth: 2

task
result
verifier
```
