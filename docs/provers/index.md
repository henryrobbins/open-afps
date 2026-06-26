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

## How the agent provers work

An {class}`~open_atp.provers.agent_prover.AgentProver` composes two concerns:

- a {class}`~open_atp.harness.base.Harness` — the *agent* concern: launch script,
  credential forwarding, and output parsing (one per harness page below); and
- a {class}`~open_atp.backends.base.ComputeBackend` — the *compute* concern: where
  the agent runs, with Lean+Mathlib and the
  [lean-lsp-mcp](https://github.com/oOo0oOo/lean-lsp-mcp) server.

`prove` stages the project into the workdir, lets the agent fill the `sorry`s in
place, then diffs the `.lean` files against the staged originals to report what
changed. The shared {class}`~open_atp.verify.Verifier` does the final
compile / sorry / axiom check. Configuration fields are documented under
{class}`~open_atp.provers.agent_prover.AgentProver` in the
{doc}`../api/provers` reference.

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

## References

Several of the provers implement published methods. If you use one of them,
please cite the corresponding paper.

```bibtex
@inproceedings{requena2026a,
  title = {A Minimal Agent for Automated Theorem Proving},
  author = {Borja Requena and Austin Letson and Krystian Nowakowski and Izan Beltran Ferreiro and Leopoldo Sarra},
  booktitle = {ICLR 2026 Workshop: VerifAI-2: The Second Workshop on AI Verification in the Wild},
  year = {2026},
  url = {https://openreview.net/forum?id=E30g7bO7rU}
}

@article{achim2025aristotle,
  title = {Aristotle: IMO-level Automated Theorem Proving},
  author = {Achim, Tudor and Best, Alex and Bietti, Alberto and Der, Kevin and F{\'e}d{\'e}rico, Math{\"\i}s and Gukov, Sergei and Halpern-Leistner, Daniel and Henningsgard, Kirsten and Kudryashov, Yury and Meiburg, Alexander and others},
  journal = {arXiv preprint arXiv:2510.01346},
  year = {2025}
}

@article{liu2026numina,
  title = {Numina-Lean-Agent: An Open and General Agentic Reasoning System for Formal Mathematics},
  author = {Liu, Junqi and Zhou, Zihao and Zhu, Zekai and Santos, Marco Dos and He, Weikun and Liu, Jiawei and Wang, Ran and Xie, Yunzhou and Zhao, Junqiao and Wang, Qiufeng and others},
  journal = {arXiv preprint arXiv:2601.14027},
  year = {2026}
}
```

The agent harnesses share the [lean-lsp-mcp](https://github.com/oOo0oOo/lean-lsp-mcp)
server (all except ax-prover, which ships its own Lean tooling) and bundle vendored
Lean skills (see `vendor/`):

```bibtex
@software{lean-lsp-mcp,
  author = {Oliver Dressler},
  title = {{Lean LSP MCP: Tools for agentic interaction with the Lean theorem prover}},
  url = {https://github.com/oOo0oOo/lean-lsp-mcp},
  month = {3},
  year = {2025}
}

@software{leanprover-skills,
  author = {{Lean FRO}},
  title = {Official Agent {Skills} for developing with {Lean} 4},
  url = {https://github.com/leanprover/skills},
  year = {2025}
}

@software{lean4-skills,
  author = {Cameron Freer},
  title = {Lean 4 {Skills}: Theorem proving skill and workflow pack for {AI} coding agents},
  url = {https://github.com/cameronfreer/lean4-skills},
  month = oct,
  year = {2025}
}
```

## Citing OpenATP

If you use `OpenATP` itself, please cite the project:

```bibtex
@software{openatp,
  title = {OpenATP: Open Automated Theorem Proving},
  author = {Henry Robbins},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/henryrobbins/open-atp}
}
```
