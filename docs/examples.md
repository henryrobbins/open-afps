# Examples

OpenATP ships a handful of trivial theorem examples, each an exercise from [*Mathematics in Lean*](https://leanprover-community.github.io/mathematics_in_lean/). These are provided primarily as a convenience for testing compute and prover setup.

## Running an example

Use {func}`~open_atp.examples.example_task` to load a task from the {class}`~open_atp.examples.EXAMPLE` enum.

```{testcode}
from open_atp.backends.docker import DockerBackend
from open_atp.examples import EXAMPLE, example_task
from open_atp import standard_prover

prover = standard_prover("claude", backend=DockerBackend())
result = prover.prove(example_task(EXAMPLE.MUL_REORDER), output_dir="runs/example")

assert result.success
```

## Available examples

(MUL_REORDER)=
### `MUL_REORDER`

```{literalinclude} ../src/open_atp/examples/assets/MulReorder.lean
:language: lean
```

### `ABS_MUL_LT`

```{literalinclude} ../src/open_atp/examples/assets/AbsMulLt.lean
:language: lean
```

### `INTER_SUBSET`

```{literalinclude} ../src/open_atp/examples/assets/InterSubset.lean
:language: lean
```

### `INTER_UNION_DISTRIB`

```{literalinclude} ../src/open_atp/examples/assets/InterUnionDistrib.lean
:language: lean
```

### `SMUL_ADD`

```{literalinclude} ../src/open_atp/examples/assets/SmulAdd.lean
:language: lean
```
