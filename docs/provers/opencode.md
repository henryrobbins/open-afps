# OpenCode

```{include} _meta_opencode.md
:parser: myst
```

Use [OpenCode](https://opencode.ai/) as an automated theorem prover with Lean skills and MCP tooling. This prover uses the {class}`~open_atp.provers.agent_prover.AgentProver` with the {class}`~open_atp.harness.opencode.OpenCodeHarness`. Unlike Claude Code and Codex, OpenCode is provider-agnostic: one CLI fronts Anthropic, OpenAI, Google, or DeepSeek models.

## Authentication

OpenCode bills directly against an API provider rather than a flat-rate subscription. Sign up for an API account with your chosen provider, fund it, and find the full provider list at [OpenCode providers](https://opencode.ai/docs/providers/). By default the harness reads the provider's key from the host environment, for example:

```bash
export DEEPSEEK_API_KEY=...
```

It is recommended to define this in a `.env` file in your project root. Alternatively, pass the key matching your chosen provider to the harness explicitly:

```python
OpenCodeHarness(model="claude-opus-4-8", provider_api_key="sk-...")
```

The provider is inferred from the model prefix unless you pass `provider` explicitly. Either way the harness forwards the key into the sandbox under its canonical env var (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`, or `DEEPSEEK_API_KEY`). See {ref}`tracking-cost-and-usage-opencode` for details.

## Using the prover

### Standard prover via Python API

The simplest way to run the prover is through {func}`~open_atp.config.standard_prover` which uses a standard configuration pointing at a DeepSeek model. Either set `DEEPSEEK_API_KEY` in the host environment or pass it explicitly to the harness. Here, we prove the {ref}`MUL_REORDER` example theorem:

```python
from pathlib import Path

from open_atp.backends.docker import DockerBackend
from open_atp.config import standard_prover
from open_atp.examples import EXAMPLE, example_task

task = example_task(EXAMPLE.MUL_REORDER)
prover = standard_prover("opencode", backend=DockerBackend())
result = prover.prove(task, output_dir=Path("demo"))
```

### Standard prover via CLI

The standard prover can also be run from the CLI:

```bash
open-atp prove path/to/task.lean output_dir opencode
```

### Customizing the prover

To override knobs like `model` and `effort`, construct the class directly. The `provider` is inferred from the model prefix unless set explicitly:

```python
from pathlib import Path

from open_atp.backends.docker import DockerBackend
from open_atp.examples import EXAMPLE, example_task
from open_atp.harness import OpenCodeHarness
from open_atp.images import DEFAULT_IMAGE
from open_atp.provers import AgentProver

task = example_task(EXAMPLE.MUL_REORDER)
prover = AgentProver(
    harness=OpenCodeHarness(model="claude-opus-4-8", effort="medium"),
    backend=DockerBackend(image=DEFAULT_IMAGE),
)
result = prover.prove(task, output_dir=Path("demo"))
```

:::{tip}
If you are harness agnostic and want to use Anthropic or OpenAI models, it is recommended to use the {doc}`/provers/claude_code` or {doc}`/provers/codex`  provers. These provers are billed against subscription plans rather than API usage, which is often much cheaper.
:::

## Harness details

By default, the OpenCode harness is equipped with:

- Official Lean skills {cite:p}`leanprover_skills`.
- `lean-lsp-mcp` MCP server {cite:p}`lean_lsp_mcp`.

The agent prompt (below) is written into the working directory and read into `$PROMPT`. The OpenCode CLI is then invoked in non-interactive mode with `$PROMPT` as the input. See the script below for the full OpenCode CLI invocation.

:::{dropdown} Agent Prompt
:icon: book
```{literalinclude} ../../src/open_atp/provers/agent_prover.py
:language: text
:start-after: PROVER_PROMPT = """
:end-before: END PROVER_PROMPT
```
:::

:::{dropdown} `src/open_atp/harness/assets/scripts/opencode_agent.sh`
:icon: code
```{literalinclude} ../../src/open_atp/harness/assets/scripts/opencode_agent.sh
:language: bash
```
:::

(tracking-cost-and-usage-opencode)=
## Tracking cost and usage

The OpenCode CLI reports a per-step cost and token breakdown for each provider call. The cost is summed to populate `cost_usd` in {class}`~open_atp.provers.base.ProofResult`. You can also monitor consumption from your provider's usage dashboard. For example, DeepSeek's dashboard is at [DeepSeek Usage](https://platform.deepseek.com/usage).
