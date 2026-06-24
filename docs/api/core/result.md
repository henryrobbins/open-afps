# `core.result`

The output types: the verification report, the pre-verification generation output,
and the per-prover proof result.

```{eval-rst}
.. autoclass:: open_afps.core.result.VerificationReport
   :exclude-members: compiles, sorry_free, axioms, compile_log, per_file, non_standard_axioms, verified

.. autoclass:: open_afps.core.result.GenerationOutput
   :no-members:

.. autoclass:: open_afps.core.result.ProofResult
   :exclude-members: prover, verification, completed_files, cost_usd, duration_s, logs, artifacts_dir, logs_dir, metadata, error, success

.. autodata:: open_afps.core.result.STANDARD_AXIOMS
```
