Carefully read the prompts under `.claude/prompts/subagent_prompts/` (common.md, coordinator.md, proof_agent.md, informal_agent.md, golfer.md).
Also read `.claude/skills/SKILL.md` and each sub-skill's `SKILL.md` (search, verification, llm, code-transform, sorrifier) so you know which local CLI tools are available and how to invoke them.

You should act as coordinator agent to complete the target folder / file.

When you launch a subagent, you MUST:

1. **Describe the assigned task clearly** in the prompt
2. **Include the absolute path** to its corresponding prompt file and instruct it to read and follow that prompt
3. **Include the absolute path** to the reference resources (listed below) and instruct it to read them -- they are written by expert mathematicians and are critical for the proof
4. **Instruct the subagent** to update its own target entry in CHECKLIST.md after making any progress
5. Tell the subagent to make good use of the local CLI skills in `.claude/skills/cli/` — in particular `leanexplore.py` (semantic mathlib search, invoked as `uv run --no-project .claude/skills/cli/leanexplore.py QUERY`) and `discussion_partner.py` (ask Gemini / GPT for proof strategy hints). All verification must go through `lean_check.py` (never `lake build` for per-file checks).

After a subagent returns, you MUST update CHECKLIST.md to reflect the result.

You can spawn multiple subagents simultaneously to complete the tasks. (at most 2 subagent in parallel). But MAKE SURE each subagent is working on EXACTLY ONE task.

reference resources:

Read the environment variable `REFERENCE_RESOURCES` to get the absolute path(s) of the reference material. Run:

```bash
echo "$REFERENCE_RESOURCES"
```

(or in Python: `os.environ.get("REFERENCE_RESOURCES")`). The value may be a single path or a colon-separated list of paths. If the variable is empty/unset, proceed without external references.

You should give the resolved path(s) in the prompt to the subagent.
