# discussion-partner — Discuss with Gemini/GPT

Free-form discussion about proof strategies, Lean code, math problems, or anything else related to theorem proving.

## CLI Invocation

```bash
uv run --no-project .claude/skills/cli/discussion_partner.py [QUESTION] [OPTIONS]
```

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `QUESTION` | no | stdin | Question or context to discuss. Omit or use `-` to read from stdin |
| `--file FILE` | no | — | Read question from a file (safest for text with special characters) |
| `--backend` | no | `gemini` | LLM backend: `gemini` or `gpt` |
| `--model` | no | auto | Model name. Default: `gemini-3.1-pro-preview` (gemini) or `gpt-5.2-pro` (gpt) |

## Examples

```bash
# Simple inline question
uv run --no-project .claude/skills/cli/discussion_partner.py "How should I approach this induction proof?" --backend gemini

# Pipe a .lean file — gives the model full proof context
cat stuck_proof.lean | uv run --no-project .claude/skills/cli/discussion_partner.py --backend gemini

# Use --file to avoid shell escaping issues with special characters ($, `, quotes, Unicode)
echo "What does ⊢ n + 0 = n mean?" > /tmp/q.txt
uv run --no-project .claude/skills/cli/discussion_partner.py --file /tmp/q.txt --backend gpt

# Heredoc — safe for multi-line or special-char input
uv run --no-project .claude/skills/cli/discussion_partner.py --backend gemini <<'EOF'
Proof state: ⊢ ∀ n : ℕ, n + 0 = n
What tactic should I use?
EOF
```

## Notes

- `GEMINI_API_KEY` is required when using `--backend gemini`.
- `OPENAI_API_KEY` is required when using `--backend gpt`.
- **For questions with special characters** (`$`, backticks, `"`, Unicode symbols like `⊢ ∀ ∃`), use `--file` or heredoc stdin instead of a positional argument — the shell will otherwise expand or truncate them.
- Use this tool when you are stuck and want high-level strategic advice before searching for specific lemmas.
