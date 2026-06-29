# Examples

The package ships a handful of tiny example tasks — each a single `sorry`'d exercise
from [*Mathematics in Lean*](https://leanprover-community.github.io/mathematics_in_lean/).
They double as a setup smoke test: {func}`~open_atp.examples.example_task` stages one
into the pinned Mathlib skeleton (via {func}`~open_atp.lean.create_project`) and hands you
a ready-to-run {class}`~open_atp.lean.ProofTask`.

```python
import tempfile

from open_atp.backends.docker import DockerBackend
from open_atp.examples import EXAMPLE, example_task
from open_atp import standard_prover

prover = standard_prover("claude", backend=DockerBackend())
result = prover.prove(example_task(EXAMPLE.MUL_REORDER), tempfile.mkdtemp())
print("success:", result.success)
```

Pass any {class}`~open_atp.examples.EXAMPLE` member. The bundled exercises are:

(MUL_REORDER)=
## `MUL_REORDER`

C02 "Calculating" — reorder a product of reals.

```{literalinclude} ../src/open_atp/examples/assets/MulReorder.lean
:language: lean
```

## `ABS_MUL_LT`

C03 "Logic" — a product of two reals, each smaller in absolute value than a small
`ε`, is itself smaller than `ε`.

```{literalinclude} ../src/open_atp/examples/assets/AbsMulLt.lean
:language: lean
```

## `INTER_SUBSET`

C04 "Sets and Functions" — intersecting both sides of a subset relation with the
same set preserves it.

```{literalinclude} ../src/open_atp/examples/assets/InterSubset.lean
:language: lean
```

## `INTER_UNION_DISTRIB`

C04 "Sets and Functions" — intersection distributes over union.

```{literalinclude} ../src/open_atp/examples/assets/InterUnionDistrib.lean
:language: lean
```

## `SMUL_ADD`

C09 "Linear Algebra" — scalar multiplication distributes over vector addition in a
module.

```{literalinclude} ../src/open_atp/examples/assets/SmulAdd.lean
:language: lean
```
