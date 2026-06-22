# lean-check — Local Compile Check

Check if Lean code compiles without errors using `lake env lean`. Runs locally — no API key needed.

## CLI Invocation

```bash
uv run --no-project .claude/skills/cli/lean_check.py FILE [OPTIONS]
```

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `FILE` | yes | — | Lean file path to check |
| `--timeout-seconds` | no | 120 | Max execution time (default: 120) |

## Output

Returns JSON:
- `okay` (bool) — whether the file compiled without errors
- `lean_messages` — list of errors, warnings, and infos with line numbers (`file_name`, `line`, `column`, `severity`, `data`)
- `failed_declarations` — list of theorem/definition names that failed

## Examples

```bash
uv run --no-project .claude/skills/cli/lean_check.py proof.lean
uv run --no-project .claude/skills/cli/lean_check.py proof.lean --timeout-seconds 300
```

## Notes

- No `--environment` flag needed — automatically detects the Lean project root by finding `lean-toolchain`.
- Runs `lake env lean` locally, so the project must have been built at least once (`lake build` or `lake exe cache get`).
- No API key required.
- Multiple checks can run in parallel (each is an independent process).
