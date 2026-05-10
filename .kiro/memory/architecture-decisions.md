# Architecture Decisions Log

Auto-updated after every architectural decision.

---

## Decision 1: Use TypedDict for State Schema
**Date:** May 8, 2026 (Day 1, TASK-002)  
**Decision:** Use TypedDict instead of Pydantic BaseModel for ContextFlowState  
**Why:** 
- Lightweight (no runtime overhead)
- Type hints for IDE autocomplete
- LangGraph natively supports TypedDict
- No validation overhead (we validate in nodes)

**Alternatives Rejected:**
- Pydantic BaseModel (too heavy, runtime validation not needed)
- Plain dict (no type safety)

**Impact:** Clean state management, good developer experience

---

## Decision 2: Use Groq API (Free Tier)
**Date:** May 8, 2026 (Day 1, TASK-004)  
**Decision:** Use Groq API with Llama models instead of OpenAI  
**Why:**
- Free tier available
- Fast inference (< 1 second)
- Llama 4 Scout Vision for screenshots
- Llama 3.3 70B for text reasoning

**Alternatives Rejected:**
- OpenAI GPT-4 Vision (expensive, $0.01/image)
- Google Gemini API (rate limits on free tier)
- Local models (too slow on M1)

**Impact:** Zero API cost, fast responses, good accuracy

---

## Decision 3: Separate Vision and Text Agents
**Date:** May 9, 2026 (Day 2, TASK-004 & TASK-005)  
**Decision:** Use 2 agents (Observer + Guide) instead of 1  
**Why:**
- Vision models bad at reasoning
- Text models bad at vision
- Separation of concerns
- Can swap models independently

**Alternatives Rejected:**
- Single agent doing both (worse results, higher cost)
- 3+ agents (unnecessary complexity)

**Impact:** Better results, modular design, easier to debug

---

## Decision 4: LangGraph for Orchestration
**Date:** May 10, 2026 (Day 3, TASK-007)  
**Decision:** Use LangGraph StateGraph instead of manual orchestration  
**Why:**
- Automatic routing between nodes
- Conditional edges for smart decisions
- Error handling built-in
- Easy to extend (add node + edge)

**Alternatives Rejected:**
- Manual function calls (no error handling, hard to extend)
- LangChain LCEL (less control over routing)
- Custom orchestration (reinventing the wheel)

**Impact:** Robust workflow, easy to maintain, scalable

---

## Decision 5: Conditional Edge for Error Handling
**Date:** May 10, 2026 (Day 3, TASK-009)  
**Decision:** Check for errors in conditional edge, exit on error  
**Why:**
- Prevents infinite loops
- Graceful degradation
- User sees error message, not crash

**Alternatives Rejected:**
- Retry on all errors (infinite loop risk)
- Crash on error (bad user experience)

**Impact:** Fixed infinite loop bug, robust error handling

---

=== END ARCHITECTURE DECISIONS ===
