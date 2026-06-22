# Provers

A prover is a *candidate generator*: it takes a
{class}`~open_afps.core.task.ProofTask` and produces completed Lean files. The base
{class}`~open_afps.core.prover.AutomatedProver` owns the shared lifecycle — generate,
then verify in the sandbox — so every prover gets the same final check for free.

| Prover | Generation | Credential |
| --- | --- | --- |
| [AgentProver](agent.md) | coding agent + lean-lsp-mcp in a sandbox | harness credential |
| [NuminaProver](numina.md) | AgentProver (Claude) + Numina assets + round loop | harness + helper API keys |
| [AristotleProver](aristotle.md) | Harmonic's hosted Aristotle API | `ARISTOTLE_API_KEY` |

All three subclass {class}`~open_afps.core.prover.AutomatedProver` and funnel their
output through the shared {class}`~open_afps.core.verifier.Verifier`.

```{toctree}
:maxdepth: 1

agent
numina
aristotle
```
