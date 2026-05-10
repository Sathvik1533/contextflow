# Interview Prep — ContextFlow

Auto-updated after every task with concepts, questions, and answers.

---

## TASK-002: State Schema

**Concept I Should Know Cold:**
"State is a TypedDict that acts as shared memory between agents. Each agent reads what it needs and writes its results back. LangGraph automatically merges the updates."

**Interview Question:**
"How do your agents communicate with each other?"

**My Answer:**
"Through a shared TypedDict called ContextFlowState. It's like a notebook passed between runners in a relay race. Each agent receives the state, reads the fields it needs, adds its output, and returns a dict with updates. LangGraph merges the dict into the state automatically. For example, capture_node writes screenshot_b64, observer_node reads screenshot_b64 and writes extracted_context, and guide_node reads extracted_context and writes guidance."

---

## TASK-004: Observer Agent

**Concept I Should Know Cold:**
"Vision models sometimes return JSON wrapped in markdown fences. Always strip fences with regex before parsing. Never trust LLM output format."

**Interview Question:**
"What was your biggest technical challenge with the Observer agent?"

**My Answer:**
"Groq deprecated Llama 3.2 Vision models mid-development. I had to migrate to Llama 4 Scout in 30 minutes with zero downtime. I also had to handle non-deterministic output — the Vision model sometimes returned JSON wrapped in markdown fences like ```json...```. I used regex to strip the fences before parsing, and strict schema validation to catch errors early."

---

## TASK-005: Guide Agent

**Concept I Should Know Cold:**
"Separate vision and text agents. Vision models excel at extraction, text models excel at reasoning. Using both gives better results and lower cost."

**Interview Question:**
"Why use two agents instead of one?"

**My Answer:**
"Separation of concerns. Vision models are great at extracting content from images but bad at reasoning. Text models are great at reasoning but can't process images. By using both, I get the best of both worlds. The Observer (Vision) extracts structured data, and the Guide (Text) generates actionable advice. This also makes the system modular — I can swap models independently without rewriting everything."

---

## TASK-007: LangGraph Assembly

**Concept I Should Know Cold:**
"Conditional edges separate routing logic from business logic. Nodes focus on their job, the graph handles orchestration."

**Interview Question:**
"Why use LangGraph instead of manual function calls?"

**My Answer:**
"LangGraph provides automatic orchestration, error handling, and conditional routing. With manual function calls, I'd have to write all the orchestration logic myself — if/else statements, error handling, retry logic, loop control. With LangGraph, I just define nodes and edges, and it handles the rest. Adding a new agent is just 2 lines: add_node and add_edge. It's also declarative — the graph structure is clear and easy to understand."

---

## TASK-009: Integration Test

**Concept I Should Know Cold:**
"Always check for errors in conditional edges. If you don't, a failing node can cause an infinite loop."

**Interview Question:**
"Tell me about a bug you found and fixed."

**My Answer:**
"During integration testing, I discovered an infinite loop bug. The Observer agent failed (fake data), tried to retry, failed again, and looped 10,007 times before LangGraph killed it. The issue was in the conditional edge — I was checking confidence but not checking for errors. The fix was one line: if state.get('error'): return END. This checks for errors first and exits gracefully instead of retrying forever. It taught me that error handling must be explicit, not assumed."

---

=== END INTERVIEW PREP ===


---

## DAY 3 FIX: Observer Priority Rule

**Concept I Should Know Cold:**
"Prompt engineering can solve multi-window scenarios without code changes. When both browser and terminal are visible, explicit priority rules guide the AI."

**Interview Question:**
"How did you handle the case where multiple windows are visible on screen?"

**My Answer:**
"I encountered a problem where the Observer was analyzing terminal code instead of browser content when both were visible. Instead of writing complex window detection code, I solved it with prompt engineering. I added a PRIORITY RULE to the Observer prompt: 'If browser + terminal visible → analyze browser, ignore terminal.' This worked immediately and proved ContextFlow works on ANY content (sports, news, tech), not just technical content. For the future, I plan to make this dynamic by passing user_intent to Observer — if the user says 'explain this cricket match,' prioritize browser; if they say 'debug this error,' prioritize terminal."

---

=== END INTERVIEW PREP ===
