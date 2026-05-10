# .kiro/hooks/git-discipline.md
# Kiro reads this and applies git rules after every file write.

## On Every File Write/Edit

After writing or modifying any .py file:
1. Run: git status (show what changed)
2. Run: git diff --stat
3. Suggest commit message: "type: description"
4. Ask user: "Commit these changes? y/n"
5. Only commit on explicit "y"

NEVER auto-commit. NEVER push without "push" instruction.

## Commit Type Reference

| Type | When |
|------|------|
| feat | new function, node, agent, or feature |
| fix | bug fix |
| refactor | restructure without behavior change |
| docs | README, comments, docstrings |
| chore | setup, config, dependencies |
| test | adding or fixing tests |

## Session End Checklist

Before closing session:
- [ ] All changes committed
- [ ] No .env in git history (check with: git log --all --full-history -- .env)
- [ ] Write session summary to .kiro/memory/session-log.md
