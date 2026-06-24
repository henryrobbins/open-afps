# `core.result`

The output types: the verification report and the per-prover proof result.

```{eval-rst}
.. autoclass:: open_atp.core.result.VerificationReport
   :exclude-members: compiles, sorry_free, axioms, compile_log, per_file, non_standard_axioms, verified

.. autoclass:: open_atp.core.result.ProofResult
   :exclude-members: prover, verification, output_dir, completed_files, cost_usd, duration_s, metadata, error, wd, logs_dir, success

.. autodata:: open_atp.core.result.STANDARD_AXIOMS
```
