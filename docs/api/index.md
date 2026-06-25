# API Reference

The reference mirrors the package layout under `src/open_atp/`:

- {doc}`provers` — `open_atp.provers`: the prover registry ({data}`~open_atp.provers.PROVER_TYPES`, {func}`~open_atp.provers.get_prover`, {func}`~open_atp.provers.available_provers`), the `AutomatedProver` base, its `ProofResult` output, and the concrete candidate generators.
- {doc}`lean` — `open_atp.lean`: the Lean input contract (`LeanProject`, `ProofTask`) and the `stage_files` helper.
- {doc}`verify` — `open_atp.verify`: the `VerificationReport` and the shared `Verifier`.
- {doc}`backends` — `open_atp.backends`: the `ComputeBackend` sandbox primitive (`docker` | `modal`).
- {doc}`harness` — `open_atp.harness`: the agent-CLI harnesses composed by `AgentProver`.

```{toctree}
:maxdepth: 2

provers
lean
verify
backends
harness
```
