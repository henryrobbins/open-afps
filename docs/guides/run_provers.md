# Running a prover

A prover takes a {class}`~open_atp.lean.ProofTask` (a lake project plus
optional instructions and target files) and returns a
{class}`~open_atp.provers.base.ProofResult` (the completed files, a
{class}`~open_atp.verify.VerificationReport`, cost, and duration). Every prover
shares the same lifecycle: **generate candidate files, then verify them in a sandbox**
via the shared {class}`~open_atp.verify.Verifier`.

## Prerequisites

- Docker running and the `open-atp:latest` image built (see
  {doc}`docker`).
- A credential for the prover you choose — each prover's page under
  {doc}`../provers/index` lists the environment variable(s) it needs.

## Filling sorrys with a prover

{func}`~open_atp.config.standard_prover` builds any of the catalog provers against a
backend with its baked-in defaults — pick a name from
{func}`~open_atp.config.standard_provers` and run it:

```python
from pathlib import Path

from open_atp.backends.docker import DockerBackend
from open_atp.config import standard_prover
from open_atp.images import DEFAULT_IMAGE
from open_atp.lean import LeanProject, ProofTask

backend = DockerBackend(image=DEFAULT_IMAGE)
prover = standard_prover("agent:claude", backend=backend)

task = ProofTask(project=LeanProject("path/to/lake/project"))
result = prover.prove(task, output_dir=Path("runs/demo"))

print("success:", result.success)
print("cost_usd:", result.cost_usd)
print("duration_s:", result.duration_s)
```

`prove` populates `output_dir/{wd,logs}/`: `wd` is the completed lake project and
`logs` holds the run record (`stdout.txt`, `stderr.txt`, `result.json`).

Swap `"agent:claude"` for any catalog name (`"agent:codex"`, `"agent:opencode"`,
`"agent:vibe"`, `"agent:axprover"`, `"numina"`, `"aristotle"`) to switch prover. Each
needs its own credential — see the per-prover pages under {doc}`../provers/index`. To
customize a knob (model, effort, skills, ...), use
{func}`~open_atp.config.build_prover` with a full config dict instead.

## From the command line

The `open-atp prove` command is a thin shell over the same API: pick a prover, point
at the work, and choose where the `{wd,logs}` output lands. It runs on the local
Docker backend with the default image (see {doc}`docker`).

The work can be a lake project directory **or** a single bare `.lean` file — a bare
file is staged into the pinned Mathlib skeleton for you:

```console
$ open-atp prove agent:claude MyFile.lean runs/demo
agent             ✓ verified                   cost=$0.0123  time=42s
output: runs/demo
```

The completed file lands in `runs/demo/wd/`. Add `--json` to emit the full
{class}`~open_atp.provers.base.ProofResult` as JSON. The prover argument is any
catalog name; `--help` lists them. See {doc}`../cli` for the full reference.

A bare file only works for the skeleton's pinned toolchain and Mathlib revision; a
file needing a different revision or extra dependencies must arrive as a full lake
project directory instead.

## Inspecting the result

A {class}`~open_atp.provers.base.ProofResult` records everything a run produced:

```python
result.prover            # "agent" | "aristotle" | "numina"
result.success           # compiles, sorry-free, no foreign axioms
result.completed_files   # {relative path -> new file contents}
result.verification      # VerificationReport (per-file compile, axioms, log)
result.cost_usd          # estimated USD, when the prover reports it
result.duration_s        # wall-clock seconds
result.output_dir        # the run's output dir
result.wd                # output_dir/wd  -- the completed lake project
result.logs_dir          # output_dir/logs -- stdout.txt, stderr.txt, result.json
```

The {class}`~open_atp.verify.VerificationReport` exposes the individual
sub-checks behind `success`: whether the project `compiles`, whether it is
`sorry_free`, and which `axioms` the proofs depend on (anything outside
{data}`~open_atp.verify.STANDARD_AXIOMS` means the proof is not actually
complete).

To run several provers across several tasks and compare them, see
{doc}`benchmark`.
