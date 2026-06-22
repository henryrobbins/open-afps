# leansearch — Natural Language + Lean Term Search

Searches Lean theorems using natural language descriptions or Lean terms.

## CLI Invocation

```bash
uv run --no-project .claude/skills/cli/leansearch.py QUERY [-n NUM_RESULTS]
```

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `QUERY` | yes | — | Natural language description or Lean terms |
| `-n, --num-results` | no | 5 | Maximum number of results |

## Examples

```bash
uv run --no-project .claude/skills/cli/leansearch.py "commutativity of addition for natural numbers"
uv run --no-project .claude/skills/cli/leansearch.py "List.map preserves length" -n 8
uv run --no-project .claude/skills/cli/leansearch.py "Nat.add_comm"
```

## Notes

- Accepts both plain English and Lean identifier/term queries.
- Complements `leanexplore` and `leanfinder`; use multiple search tools in parallel when unsure which lemma name to look for.
