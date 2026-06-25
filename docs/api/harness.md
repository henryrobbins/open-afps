---
tocdepth: 3
---

# `harness`

The `open_atp.harness` package is the *agent* concern composed by the
{class}`~open_atp.provers.agent_prover.AgentProver`: for one agent CLI it owns the
launch script, credential forwarding, asset staging, and token/cost parsing. The
*compute* concern (where the command runs, with Lean+Mathlib) lives in the injected
{class}`~open_atp.backends.base.ComputeBackend`.

See the per-harness prover pages under {doc}`../provers/index` for credential setup.

## Base

```{eval-rst}
.. autoclass:: open_atp.harness.base.Harness
   :exclude-members: name

.. autoclass:: open_atp.harness.base.HarnessConfig

.. autoclass:: open_atp.harness.base.HarnessRunResult
   :no-members:

.. autoclass:: open_atp.harness.base.AuthSpec
   :no-members:
```

## Harnesses

Each harness adapts one agent CLI and pairs with a
{class}`~open_atp.harness.HarnessConfig` subclass (set as
{class}`~open_atp.provers.agent_prover.AgentProverConfig`'s `harness`). The runtime
harnesses are registered in {data}`~open_atp.harness.HARNESSES` and their configs in
{data}`~open_atp.harness.HARNESS_CONFIGS`, both keyed by `name`.

```{eval-rst}
.. autoclass:: open_atp.harness.claude_code.ClaudeCodeHarness
   :show-inheritance:
   :exclude-members: stage, name

.. autoclass:: open_atp.harness.claude_code.ClaudeCodeHarnessConfig
   :show-inheritance:
   :no-members:

.. autoclass:: open_atp.harness.codex.CodexHarness
   :show-inheritance:
   :exclude-members: stage, name

.. autoclass:: open_atp.harness.codex.CodexHarnessConfig
   :show-inheritance:
   :no-members:

.. autoclass:: open_atp.harness.opencode.OpenCodeHarness
   :show-inheritance:
   :exclude-members: stage, name

.. autoclass:: open_atp.harness.opencode.OpenCodeHarnessConfig
   :show-inheritance:
   :no-members:

.. autoclass:: open_atp.harness.vibe.VibeHarness
   :show-inheritance:
   :exclude-members: stage, name

.. autoclass:: open_atp.harness.vibe.VibeHarnessConfig
   :show-inheritance:
   :no-members:

.. autoclass:: open_atp.harness.axprover.AxProverHarness
   :show-inheritance:
   :exclude-members: stage, name

.. autoclass:: open_atp.harness.axprover.AxProverHarnessConfig
   :show-inheritance:
   :no-members:

.. autodata:: open_atp.harness.HARNESSES

.. autodata:: open_atp.harness.HARNESS_CONFIGS
```

## Asset bundles

An {class}`~open_atp.harness.bundles.AssetBundle` is the selectable preset of the
*non-list* workdir assets — `extra_dirs` and the legacy `skills_dir` whole-directory
mount (both Numina-only today) — selected via `AgentProverConfig.assets`. Skills are a
list on `AgentProverConfig.skills` (staged by the prover), plugins a list on
`ClaudeCodeHarnessConfig.plugins` (Claude-only), and the prompt is owned by the prover
and the task — none are bundle concerns.

```{eval-rst}
.. autoclass:: open_atp.harness.bundles.AssetBundle
   :no-members:

.. autofunction:: open_atp.harness.bundles.resolve_bundle

.. autodata:: open_atp.harness.bundles.BUNDLES

.. autodata:: open_atp.harness.bundles.DEFAULT_BUNDLE
```

## Pricing

```{eval-rst}
.. autofunction:: open_atp.harness.cost.compute_cost_usd

.. autodata:: open_atp.harness.cost.COST_PER_MTOK
```
