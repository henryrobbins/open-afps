(prover-numina)=
# NuminaProver

The {class}`~open_afps.provers.numina.NuminaProver` is a configured variant of the
{class}`~open_afps.provers.agent.prover.AgentProver`. Structurally, Numina is
"Claude Code + a specific skills/prompts/search toolkit, run in a multi-round loop in
a sandbox", so rather than re-implement it, `open-afps` extends `AgentProver` pinned
to the `claude_code` harness with Numina's vendored assets and adds the two genuinely
different behaviours:

- a **round-continuation loop** — re-invoke the agent while it reports it hit a limit
  rather than completing; and
- the **statement tracker** — guard against the agent deleting or weakening the
  theorems it was asked to prove.

Numina's helper skills call out to Leandex / Gemini / GPT, so its config carries
those API keys
({attr}`~open_afps.provers.numina.NuminaProverConfig.helper_env_keys`) to forward
into the sandbox.

:::{warning}
The `NuminaProver` is currently a **stub**:
{meth}`~open_afps.provers.numina.NuminaProver.prove` raises `NotImplementedError`.
The config surface below is stable, but the round loop and statement tracker are
still being implemented.
:::

## Configuration

```python
from open_afps.provers.numina import NuminaProverConfig
from open_afps.images import DEFAULT_IMAGE, DEFAULT_TOOLCHAIN

config = NuminaProverConfig(
    image=DEFAULT_IMAGE,
    supported_toolchain=DEFAULT_TOOLCHAIN,
    max_rounds=20,
    guard_statements=True,
)
```

The `harness` is fixed to `claude_code` and `assets` to `numina`. See
{class}`~open_afps.provers.numina.NuminaProverConfig` in the {doc}`../api/provers`
reference for the full set of fields.
