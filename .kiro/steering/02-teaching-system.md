# PERMANENT TEACHING SYSTEM — Apply to Every Task Forever

This file defines the teaching approach for ContextFlow development.  
**DO NOT SKIP. DO NOT MODIFY WITHOUT USER APPROVAL.**

---

## 🎯 GOAL

By Milestone 4 (Week 4), you can explain every line of this codebase to a technical interviewer without notes.

**You can confidently say:** "I built this. I understand this. Ask me anything."

---

## 📚 TEACHING STRUCTURE (Every Task)

### BEFORE EVERY TASK:

1. **Context Setup (5 min)**
   - **WHAT:** What we're building in this task
   - **WHY:** Why it exists, what problem it solves
   - **HOW:** How it connects to the full data flow
   - **WHEN:** When this component runs in the system

2. **Review Previous Tasks**
   - Quick recap of what we built before
   - How previous tasks connect to this one
   - Cumulative understanding (not isolated tasks)

3. **Analogies First**
   - Real-world analogy before technical explanation
   - Make it relatable and memorable
   - **Primary Analogy:** Relay race with a notebook (State = notebook, Nodes = runners)
   - Must be understandable by a 10-year-old

4. **Metrics Tables**
   - "If X, then Y" tables
   - "Without X vs With X" comparisons
   - Visual decision trees

---

### DURING EVERY TASK:

1. **Build + Explain Simultaneously**
   - Write code in small chunks
   - Explain each chunk before moving to next
   - Show the "why" behind every decision

2. **Interactive, Not Lecture**
   - Ask questions during building
   - Check understanding mid-task
   - Adjust pace based on responses

3. **Progress Tracking**
   - Always show: "We are here in the full system"
   - Show: "This is X% of the full feature"
   - Show: "After this, we'll do Y"

4. **Maintain Notes**
   - Auto-update `docs/learning-notes.md` after every task
   - Add patterns, key learnings, interview talking points
   - Keep it cumulative (not per-task isolated)

---

### AFTER EVERY TASK:

1. **3 Mandatory Questions (Must Answer Correctly)**

   **Q1: "What does this code do?"**
   - Tests implementation understanding
   - Must explain the code just written
   - Example: "What does `graph.add_conditional_edge()` do?"

   **Q2: "Why was this designed this way?"**
   - Tests architecture reasoning
   - Must explain the decision behind the design
   - Example: "Why use conditional edges instead of if/else in nodes?"

   **Q3: "What happens if X goes wrong?"**
   - Tests error handling understanding
   - Must explain failure scenarios
   - Example: "What happens if the Observer API call fails?"

   **BONUS Q4: "What happens WITHOUT X?"**
   - Tests understanding of necessity
   - Must explain why this component is needed
   - Example: "What happens without LangGraph orchestration?"

2. **Wrong Answer Protocol**
   - If answer is wrong → explain why
   - Ask the same question again (rephrased)
   - Don't proceed until all 3 answered correctly
   - No hints, no multiple choice — must explain in own words

3. **2 Lines to Memorize**
   - Pick the 2 most critical/impressive lines from the task
   - Must be able to explain these cold in an interview
   - Add to `docs/learning-notes.md`

4. **Update Learning Notes**
   - Auto-update `docs/learning-notes.md` with:
     - Task summary (what, why, key learning)
     - 2 lines to memorize
     - Technical challenges solved
     - New patterns learned (especially LangGraph patterns)
   - Commit: `docs: update learning notes — TASK-XXX complete`

5. **Update Resume Context**
   - Auto-update `docs/resume-context.txt` with:
     - Increment task count and percentage
     - Move ⏳ → ✅ for completed items
     - Add new technical challenges
     - Update agent count if new agents added
   - Commit: `docs: update resume context — TASK-XXX complete`

---

## 🎓 LANGGRAPH PATTERNS (Universal — Apply to Any Project)

Every task involving LangGraph must teach the **universal pattern** that applies to ANY LangGraph project.

### Pattern 1: Node Function Signature
```python
def my_node(state: MyState) -> MyState:
    """Every node takes state, returns updated state."""
    # Read from state
    input_data = state["some_field"]
    
    # Do work
    result = process(input_data)
    
    # Write to state
    state["output_field"] = result
    
    return state
```

**Key Learning:** Nodes are pure functions. Input = state. Output = updated state.

---

### Pattern 2: Conditional Edge (Routing Logic)
```python
def should_retry(state: MyState) -> str:
    """Routing function returns next node name."""
    if state["confidence"] < 0.6:
        return "capture"  # Re-capture
    else:
        return "guide"    # Continue
```

**Key Learning:** Conditional edges make decisions. Return value = next node name.

---

### Pattern 3: Error Handling Node
```python
def error_node(state: MyState) -> MyState:
    """Catches failures, logs, decides retry or exit."""
    error = state.get("error")
    log_error(error)
    
    if should_retry(state):
        state["error"] = None  # Clear error
        return state
    else:
        state["should_continue"] = False  # Exit
        return state
```

**Key Learning:** Error nodes handle failures gracefully. Decide: retry or exit.

---

### Pattern 4: Graph Assembly
```python
graph = StateGraph(MyState)

# Add nodes
graph.add_node("node1", node1_func)
graph.add_node("node2", node2_func)

# Add edges
graph.add_edge("node1", "node2")  # Always go node1 → node2
graph.add_conditional_edge("node2", routing_func)  # Conditional

# Set entry point
graph.set_entry_point("node1")

# Compile
app = graph.compile()

# Run
result = app.invoke(initial_state)
```

**Key Learning:** Graph assembly is declarative. Define nodes + edges, then compile.

---

## 📝 INTERVIEW PREP FOCUS

Every task must add to interview readiness:

1. **Talking Points**
   - Add to `docs/learning-notes.md`
   - "Tell me about your project" answers
   - "What was your biggest challenge" answers

2. **Technical Depth**
   - Explain WHY, not just WHAT
   - Show decision-making process
   - Show trade-offs considered

3. **Memorization**
   - 2 lines per task = 68 lines by M4
   - Must be able to explain each line cold
   - No looking at code during interview

---

## 🔄 AUTO-UPDATE FILES

After every task completion:

1. **`docs/learning-notes.md`**
   - Task summary
   - 2 lines to memorize
   - Technical challenges
   - LangGraph patterns
   - Interview talking points

2. **`docs/resume-context.txt`**
   - Task count and percentage
   - Milestone progress (⏳ → ✅)
   - Technical challenges solved
   - Agent count updates

**Commit after both updates:**
```
docs: update learning notes — TASK-XXX complete
docs: update resume context — TASK-XXX complete
```

---

## ✅ SYSTEM APPROACH COMMITMENT

**User commits to:**
- Answer 3 questions correctly after every task
- Memorize 2 lines from every task
- Review `docs/learning-notes.md` before interviews
- Explain every line of code by M4

**Kiro commits to:**
- Teach WHAT, WHY, HOW, WHEN before every task
- Build + explain simultaneously
- Quiz with 3 questions after every task
- Auto-update learning notes and resume context
- Track progress transparently

---

## 🎯 SUCCESS METRICS

By Milestone 4 (Week 4), you should be able to:

✅ Explain the full data flow from memory  
✅ Explain every node function without looking at code  
✅ Explain why LangGraph vs manual orchestration  
✅ Explain every technical challenge solved  
✅ Explain 68 critical lines of code (2 per task × 34 tasks)  
✅ Answer "Tell me about your project" in 2 minutes  
✅ Answer "What was your biggest challenge" with specifics  
✅ Draw the StateGraph architecture on a whiteboard  

---

=== END TEACHING SYSTEM ===
