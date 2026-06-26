# OpenA⊢P

**Open Automated Theorem Proving.** Run [Lean](https://lean-lang.org/) files
containing `sorry` through leading proof-synthesis backends and get back
**verified** completed proofs with metadata (verification status, cost,
duration). Every prover — including hosted ones like Aristotle — funnels its
output through one shared {class}`~open_atp.verify.Verifier` that compiles the
candidate in a Lean+Mathlib sandbox and checks that it compiles, is sorry-free,
and is axiom-clean.

See below for installation instructions, user guides, the prover catalogue, and the
API reference.

```{toctree}
:maxdepth: 1
:caption: Contents

installation
guides/index
provers/index
datasets
examples
development/index
api/index
cli
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
