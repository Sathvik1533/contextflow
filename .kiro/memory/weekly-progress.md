# Weekly Progress Log

Auto-updated every Friday or at week completion.

---

## Week 1: Foundation (May 8-10, 2026)

### Tasks Completed (9/9 = 100%)
- ✅ TASK-000: GitHub repo setup
- ✅ TASK-001: Project scaffold (pyproject.toml, folders, .env)
- ✅ TASK-002: State schema (ContextFlowState TypedDict)
- ✅ TASK-003: Screen capture (mss → base64 PNG)
- ✅ TASK-004: Observer agent (Llama 4 Scout Vision)
- ✅ TASK-005: Guide agent (Llama 3.3 70B)
- ✅ TASK-006: Output node (rich CLI + clipboard)
- ✅ TASK-007: LangGraph assembly (StateGraph + conditional edges)
- ✅ TASK-008: Entry point (src/main.py)
- ✅ TASK-009: Integration test (all passing)

### Problems Solved
1. **Model Deprecation (Day 2):** Groq deprecated Llama 3.2 Vision mid-development → Migrated to Llama 4 Scout in 30 minutes
2. **JSON Parsing (Day 2):** Vision models return markdown fences → Regex stripping + validation
3. **Infinite Loop Bug (Day 3):** Observer fails → retries forever → Fixed with error check in conditional edge
4. **Multi-Window Priority (Day 3):** Observer analyzed terminal instead of browser → Added PRIORITY RULE to prompt
5. **Python 3.14 Syntax Errors (Day 3):** Numbered lists in docstrings broke → Changed to bullet points
6. **Observer JSON Parsing Failures (Day 3):** Prompt too complex (70 lines) → Simplified to 30 lines
7. **Browser Size Dependency (Day 3):** Observer prioritizes largest window → Workaround (make browser large), proper fix in Week 2

### What I Learned
- **LangGraph Patterns:** StateGraph, conditional edges, node functions, initial state setup
- **Multi-Agent Design:** Separation of concerns (Vision vs Text)
- **State Management:** TypedDict as shared memory (relay race notebook)
- **Error Handling:** Explicit error checks prevent infinite loops
- **Testing:** Integration tests catch bugs early
- **Prompt Engineering:** Vision models need <40 lines, long prompts = confusion
- **Debugging Methodology:** Read errors carefully, test one change at a time, simplify when stuck
- **Python Fundamentals:** Functions, dictionaries, input(), f-strings, imports
- **User Intent:** Personalization makes AI actually useful (same screen, different advice)

### Milestones Achieved
- ✅ Milestone 1: Observer returns valid JSON
- ✅ Milestone 2: Full loop working

### What's Next (Week 2)
- File Reader agent (read open files in IDE)
- Terminal Watcher agent (capture terminal output)
- Clipboard Monitor agent (track clipboard history)
- Browser Context agent (extract URLs and titles)
- Git Context agent (git status, recent commits)

### Stats
- **Code Written:** ~1000 lines (including Day 3 user intent prompt)
- **Tests:** 12 tests, all passing
- **Commits:** 15+ commits
- **Time:** 3 days (12-15 hours total, including 4 hours debugging on Day 3)
- **Debugging Time:** 4 hours (Day 3 debugging marathon)
- **Lines Debugged:** 900-line debug log created
- **LinkedIn Posts:** 3 posts (Day 1, Day 2, Day 3)
- **Instagram Stories:** 3 stories (Day 1, Day 2, Day 3)

---

=== END WEEK 1 ===
