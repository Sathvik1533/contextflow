# ContextFlow — Session Memory Log
# Kiro writes here after every session. Never delete old entries.

---

## Session Template (copy for each session)

```
## Session — [DATE] [TIME]

### What was built
- 

### What works
- 

### What failed / blockers
- 

### Decisions made
- 

### Next session starts at
TASK-00X: [task name]
```

---

## Session 001 — Project Initialized

### What was built
- Kiro steering files (global brain + ContextFlow project rules)
- Requirements spec
- Tasks spec
- Architecture docs (from Claude chat)

### What works
- Kiro has full context: architecture, milestones, code quality rules, git discipline

### What failed / blockers
- None yet. No code written.

### Decisions made
- Free tier: Google AI Studio (Gemini 2.0 Flash)
- CLI first, overlay UI at Week 5+
- Not copying lil-agents — original Python project
- Hotkey: Cmd+Shift+Space
- Clipboard: pbcopy (macOS native)

### Next session starts at
TASK-000: GitHub repo creation via MCP


---

## Session 002 — Day 3 Complete (May 12, 2026)

### What was built
- User intent prompt in `src/main.py`
- Interactive input: "What are you trying to learn right now?"
- User intent passed to all agents via initial state
- Confirmation message and graph building visibility
- Week 1 complete (9/9 tasks)

### What works
- ✅ User intent prompt collects user's learning goal
- ✅ Intent passed to agents via `initial_state["user_intent"]`
- ✅ System personalizes guidance based on intent
- ✅ Tested on ESPN cricket (proves works on ANY content)
- ✅ All Week 1 tasks complete

### What failed / blockers
- **4 hours of debugging:**
  1. Python 3.14 syntax errors (numbered lists in docstrings)
  2. Observer returning invalid JSON (prompt too complex - 70 lines)
  3. Virtual environment activation issues (pyenv conflicts)
  4. Observer analyzing terminal instead of browser

### Decisions made
- **User intent before graph:** Collected before graph runs so all agents have access
- **Default to "general learning":** Better than empty string, gives Guide some context
- **Simplified Observer prompt:** 70 lines → 30 lines (vision models need <40 lines)
- **PRIORITY RULE in prompt:** "If browser + terminal visible → analyze browser"
- **Never use Python 3.14:** Too new, use 3.11 or 3.12 for production

### Technical challenges solved
1. **Python 3.14 syntax errors:** Changed numbered lists to bullet points
2. **Observer JSON parsing:** Simplified prompt from 70 → 30 lines
3. **Multi-window priority:** Added PRIORITY RULE to Observer prompt
4. **Browser size dependency:** Workaround (make browser large), proper fix in Week 2

### Key learnings
- Vision models need SHORT prompts (<40 lines)
- Prompt engineering solves multi-window scenarios without code changes
- Debugging teaches more than smooth development
- Test incrementally (don't add 3 features at once)
- Document everything (created 900-line debug log)

### Next session starts at
Week 2, Day 4: File Reader agent (read open files in IDE)

---

=== END SESSION 002 ===
