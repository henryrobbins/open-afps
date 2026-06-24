# API Reference

The reference mirrors the package layout under `src/open_afps/`:

- {doc}`platform` — `open_afps.api`: the dispatch layer ({func}`~open_afps.api.build_prover`, {class}`~open_afps.api.Platform`, {class}`~open_afps.api.SolveResult`).
- {doc}`core/index` — `open_afps.core`: the task/result contracts and the shared verifier.
- {doc}`backends` — `open_afps.backends`: the `ComputeBackend` sandbox primitive (`docker` | `modal`).
- {doc}`provers` — `open_afps.provers`: the `AutomatedProver` base and the concrete candidate generators.
- {doc}`harness` — `open_afps.harness`: the agent-CLI harnesses composed by `AgentProver`.

```{toctree}
:maxdepth: 2

platform
core/index
backends
provers
harness
```
