# ContextFlow — Doubts Diary
**Auto-maintained log of all questions asked from Day 1 to present**

Last Updated: Day 3 (May 10, 2026, 9:46 PM)

---

## PURPOSE
This file tracks every doubt, question, and clarification asked during ContextFlow development. It shows learning progression and helps identify knowledge gaps.

---

## DAY 1 DOUBTS

### Q1: Why use uv instead of pip?
**Asked:** During project setup  
**Answer:** uv is 10-100x faster than pip for package installation and dependency resolution. Built in Rust, designed for modern Python workflows. No reason to use pip anymore.

### Q2: What is TypedDict and why use it for state?
**Asked:** During TASK-002 (State Schema)  
**Answer:** TypedDict provides type hints for dictionaries without runtime overhead. Gives autocomplete, type checking, and documentation. Better than plain dict for shared state between agents.

### Q3: Why mss instead of PIL for screenshots?
**Asked:** During TASK-003 (Screen Capture)  
**Answer:** mss is 10x faster than PIL for screen capture. PIL is for image processing (resize, encode), mss is for grabbing pixels from monitor. Use both: mss for capture, PIL for processing.

### Q4: Why base64 encode screenshots?
**Asked:** During TASK-003 (Screen Capture)  
**Answer:** Vision APIs expect images as base64-encoded strings in JSON payloads. Can't send raw binary data in JSON. Base64 converts binary → text.

### Q5: Why 2 agents (Observer + Guide) instead of 1?
**Asked:** During architecture planning  
**Answer:** Separation of concerns. Vision models excel at extracting content but are bad at reasoning. Text models excel at reasoning but can't process images. Using both gives better results and lower cost.

---

## DAY 2 DOUBTS

### Q6: Why did Groq deprecate Llama 3.2 Vision?
**Asked:** When Observer API calls started failing  
**Answer:** Groq upgraded to Llama 4 Scout (better performance, newer architecture). Deprecated old models. Had to migrate mid-development. Lesson: Always have fallback logic for API dependencies.

### Q7: Why does Observer return markdown fences sometimes?
**Asked:** During TASK-004 (Observer Agent) testing  
**Answer:** LLMs are non-deterministic. Even with "output ONLY JSON" instruction, they sometimes wrap output in ```json...```. Solution: Regex-based fence stripping + strict validation.

### Q8: What's confidence score and why does it matter?
**Asked:** During Observer schema design  
**Answer:** Confidence = how sure Observer is about its analysis (0.0-1.0). Low confidence = blurry screen, unclear content. Used for retry logic: if confidence < 0.6, re-capture screen.

### Q9: Why content-type-specific prompts for Guide?
**Asked:** During TASK-005 (Guide Agent)  
**Answer:** Different content needs different advice. YouTube tutorial → "watch this part again". Documentation → "read this section". Code → "understand this pattern". Error → "debug this issue". One-size-fits-all doesn't work.

### Q10: Why rich library for CLI output?
**Asked:** During TASK-006 (Output Node)  
**Answer:** Professional CLI output matters for user experience. rich provides colored panels, tables, progress bars, spinners. Makes CLI apps look modern, not like 1990s terminal apps.

### Q11: How does pbcopy work on macOS?
**Asked:** During clipboard integration  
**Answer:** pbcopy is macOS command-line utility that copies stdin to clipboard. `echo "text" | pbcopy` copies "text" to clipboard. Python subprocess calls pbcopy with context package string.

---

## DAY 3 DOUBTS

### Q12: Why use LangGraph instead of manual function calls?
**Asked:** During TASK-007 planning  
**Answer:** LangGraph provides automatic orchestration, error handling, conditional routing, and retry logic. It's like moving from manual assembly to an automated factory line. Easier to scale, test, and maintain.

### Q13: What's the difference between add_edge and add_conditional_edge?
**Asked:** During TASK-007 (LangGraph Assembly)  
**Answer:**
- `add_edge("A", "B")` — Always go A → B (deterministic)
- `add_conditional_edge("A", routing_func)` — Routing function decides next node based on state (dynamic)

### Q14: Why did the infinite loop happen?
**Asked:** After TASK-009 integration test revealed 10,007 iterations  
**Answer:** Conditional edge `should_retry_capture()` didn't check for errors. When Observer failed, confidence was low, so it retried forever. Fix: `if state.get("error"): return "END"`

### Q15: What's the relay race analogy?
**Asked:** During teaching system discussion  
**Answer:** State = notebook passed between runners. Each agent (runner) reads what previous agents wrote, adds their notes, passes notebook forward. LangGraph orchestrates the race automatically.

### Q16: Why does Observer analyze terminal instead of browser?
**Asked:** When testing ESPN cricket page with terminal visible  
**Answer:** Observer has no priority rule. When both browser and terminal visible, it analyzes whatever is most prominent/readable (often terminal because clear text). Solution: Add PRIORITY RULE to prompt.

### Q17: How do we guide AI priority when user has 2 things visible?
**Asked:** After fixing Observer priority rule  
**Answer:** 
- **Current (Week 1):** Assumption-based — if browser visible, prioritize browser
- **Future (Week 2+):** Intent-based — pass `user_intent` to Observer, decide priority dynamically
  - Intent: "Explain cricket match" → Prioritize browser
  - Intent: "Debug Python error" → Prioritize terminal

### Q18: Should Day 3 demo use same ESPN page as Day 2?
**Asked:** Before running Day 3 visual output  
**Answer:** YES. Same input, different orchestration. Shows progress is in HOW the system works (LangGraph orchestration, user intent prompt), not WHAT it analyzes.

### Q19: How to activate virtual environment?
**Asked:** When `python src/main.py` failed with "command not found"  
**Answer:** Must activate venv first: `source .venv/bin/activate && python src/main.py`. Without activation, system Python is used (doesn't have project dependencies).

---

## PATTERNS IN DOUBTS

### Architecture Questions (Q5, Q12, Q13)
- Focus: Why this design choice?
- Learning: Understanding tradeoffs and alternatives

### Implementation Questions (Q1, Q2, Q3, Q4, Q7, Q8, Q10, Q11, Q19)
- Focus: How does this work technically?
- Learning: Python patterns, API behavior, optimization, tooling

### Debugging Questions (Q6, Q14, Q16)
- Focus: Why did this break?
- Learning: Error handling, edge cases, testing

### Conceptual Questions (Q9, Q15, Q17, Q18)
- Focus: How do I explain/understand this?
- Learning: Analogies, teaching, user experience

---

## KNOWLEDGE GAPS IDENTIFIED

### Filled Gaps ✅
- ✅ LangGraph orchestration patterns
- ✅ Multi-agent state management
- ✅ Conditional edge routing
- ✅ Error handling in agent workflows
- ✅ Prompt engineering for structured output

### Current Gaps ⏳
- ⏳ Async/await patterns for parallel agents (Week 2)
- ⏳ LangSmith tracing for observability (Week 3)
- ⏳ Desktop overlay UI development (Week 4)
- ⏳ Window-specific capture with pyobjc (Future)

---

## AUTO-UPDATE RULES

After every task, add:
1. New doubts asked during the task
2. Answers with context
3. Related files/code if applicable
4. Pattern classification (architecture/implementation/debugging/conceptual)

**Commit message:** `docs: update doubts diary — Day X complete`

---

=== END DOUBTS DIARY ===
