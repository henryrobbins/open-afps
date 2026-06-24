# API Reference

The reference mirrors the package layout under `src/open_atp/`:

- {doc}`provers` — `open_atp.provers`: the prover registry ({class}`~open_atp.provers.PROVERS`, {func}`~open_atp.provers.get_prover`, {func}`~open_atp.provers.available_provers`), the `AutomatedProver` base, and the concrete candidate generators.
- {doc}`core/index` — `open_atp.core`: the task/result contracts and the shared verifier.
- {doc}`backends` — `open_atp.backends`: the `ComputeBackend` sandbox primitive (`docker` | `modal`).
- {doc}`harness` — `open_atp.harness`: the agent-CLI harnesses composed by `AgentProver`.

```{toctree}
:maxdepth: 2

provers
core/index
backends
harness
```
