# Provers

A prover is a *candidate generator*: it takes a
{class}`~open_atp.lean.ProofTask` and produces completed Lean files. The base
{class}`~open_atp.provers.base.AutomatedProver` owns the shared lifecycle — generate,
then verify in the sandbox — so every prover gets the same final check for free.

```{include} _table.md
:parser: myst
```

The Claude Code, Codex, OpenCode, AxProver, and Vibe provers are all the same
{class}`~open_atp.provers.agent_prover.AgentProver` composed with a different
{class}`~open_atp.harness.base.Harness`; `ID` is the
{func}`~open_atp.config.standard_prover` catalog name. Every prover subclasses
{class}`~open_atp.provers.base.AutomatedProver` and funnels its output through the
shared {class}`~open_atp.verify.Verifier`.

## Skills and tooling

The agentic harnesses are augmented with two shared resources; each prover's page
records exactly which it uses.

**lean-lsp-mcp** {cite:p}`lean_lsp_mcp` is an MCP server that exposes the Lean
language server — goal state, diagnostics, and search — as tools the agent can call
while it iterates on a proof. Every agentic harness runs it (Claude Code, Codex,
OpenCode, Vibe, and the Numina round loop, which is built on the Claude Code
harness). AxProver is the exception: it ships its own Lean tooling instead, and the
hosted AristotleProver has no local generation sandbox.

**Agent skills** are bundled prompt-and-workflow packs that teach the agent
Lean-specific tactics and conventions (see `vendor/`). Two are vendored: the
official Lean FRO skills {cite:p}`leanprover_skills`, used by Claude Code, Codex,
OpenCode, and Vibe; and Cameron Freer's `lean4` pack {cite:p}`lean4_skills`, which
Claude Code additionally loads. NuminaProver instead uses its own vendored scaffold,
and AxProver and AristotleProver use none.

```{toctree}
:maxdepth: 1
:hidden:

claude_code
codex
opencode
axprover
vibe
numina
aristotle
```
