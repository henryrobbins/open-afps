# API Reference

The reference mirrors the package layout under `src/open_afps/`:

- {doc}`provers` — `open_afps.provers`: the prover registry ({class}`~open_afps.provers.PROVERS`, {func}`~open_afps.provers.get_prover`, {func}`~open_afps.provers.available_provers`), the `AutomatedProver` base, and the concrete candidate generators.
- {doc}`core/index` — `open_afps.core`: the task/result contracts and the shared verifier.
- {doc}`backends` — `open_afps.backends`: the `ComputeBackend` sandbox primitive (`docker` | `modal`).
- {doc}`harness` — `open_afps.harness`: the agent-CLI harnesses composed by `AgentProver`.

```{toctree}
:maxdepth: 2

provers
core/index
backends
harness
```
