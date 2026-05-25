# ContextFlow — Interview Q&A
# Built from real conversation: questions asked, answers given, corrections made.
# Use this to prep for interviews. Every answer here was tested.

---

## Q1: How does `user_intent` travel from `main.py` into the Observer's prompt?

Step 1 — main.py asks the user


user_intent = input("What are you trying to learn? ")
user_intent is now a plain Python string. Lives in main.py.

Step 2 — main.py puts it into initial_state


initial_state = {
    "user_intent": user_intent,   # ← string goes into the dict
    "screenshot_b64": "",
    ...
}
graph.invoke(initial_state)
Now user_intent is inside the state dict. LangGraph takes ownership of it.

Step 3 — observer_node reads it from state

Look at src/graph/nodes.py:92:


user_intent = state.get("user_intent", "")
The node pulls it OUT of state. Now it's a local variable inside observer_node.

Step 4 — observer_node passes it to run_observer()

Look at src/graph/nodes.py:95:


extracted_context = run_observer(screenshot_b64, user_intent)
It's now a function argument being handed to the agent.

Step 5 — run_observer() injects it into the prompt

Look at src/agents/observer.py:118-125:


if user_intent:
    user_intent_instruction = f"USER INTENT: The user is trying to '{user_intent}'..."
else:
    user_intent_instruction = ""

prompt = OBSERVER_PROMPT_TEMPLATE.format(
    user_intent_instruction=user_intent_instruction
)
The string gets embedded into the prompt text. Now the Vision model sees it.

**The path:**
```
main.py (input())
  → initial_state["user_intent"]       # stored as key-value in dict
    → LangGraph carries it in state
      → observer_node: state.get("user_intent")   # node reads it
        → run_observer(screenshot_b64, user_intent)  # passed as argument
          → OBSERVER_PROMPT_TEMPLATE.format(...)     # injected into prompt
            → Groq Vision API receives it
```

**Key distinction (common mistake):**
The agent (`run_observer`) does NOT read the state directly.
The NODE reads the state, extracts the value, and passes it as a plain Python argument.
The agent only sees plain variables — never the state dict.

**Why this separation matters:**
- Agent stays pure (testable without LangGraph)
- Node is the bridge (responsible for state I/O)
- You can unit test `run_observer("fake_b64", "learning React")` with zero LangGraph setup

**Interview answer (one sentence):**
`user_intent` starts as user input in `main.py`, gets stored in `initial_state["user_intent"]`,
LangGraph carries it through state, `observer_node` pulls it out with `state.get("user_intent")`,
passes it to `run_observer()` as an argument, and `run_observer()` injects it into the prompt
template before sending to the Groq Vision API.

---

## Q2: How does LangGraph know which function to call from a string like `"guide"`?

**Think of `add_node` like saving a contact in your phone:**
```python
graph.add_node("capture", capture_node)
#               ↑              ↑
#          Name (string)   Number (function)
```

LangGraph builds an internal phonebook:
```
"capture"  →  capture_node
"observer" →  observer_node
"guide"    →  guide_node
"output"   →  output_node
```

**What happens at runtime:**
```
route_after_observer(state) returns "capture"
  → LangGraph looks up "capture" in phonebook
    → finds capture_node (the Python function)
      → calls capture_node(state)
```

**Why strings, not function references:**
```python
# WRONG — LangGraph doesn't accept this
{"guide": guide_node}

# RIGHT — LangGraph looks up "guide" in its phonebook
{"guide": "guide"}
```
The graph speaks entirely in node name strings. `add_node` is the only place
where a string name gets connected to a Python function.

**Your answer (in your own words, corrected):**
When `route_after_observer` returns `"capture"`, LangGraph looks up `"capture"`
in its internal registry (built by `add_node`), finds the Python function
`capture_node`, and calls it with the current state.

**Key distinction:** `"capture"` is the node name (string). `capture_node` is
the Python function. They are connected only through `add_node`.

---

## Q3: What failure mode does the fallback chain protect against — and what does it miss?

**The fallback chain (observer.py):**
```python
# LOOP — only wraps object creation, not API call
for model in VISION_MODELS:
    try:
        llm = ChatGroq(model=model, ...)  # no network call yet, just creates object
        break
    except:
        continue  # model name invalid → try backup

# OUTSIDE LOOP — actual API call, no fallback here
response = llm.invoke([message])  # if this fails, backup never runs
```

**What `ChatGroq()` actually does:**
Creates a client object. No network call. No API hit.
If the model name is invalid or deprecated, Groq rejects it here → loop catches it → backup runs.

**What the loop protects against:**
Invalid or deprecated model name — caught at object creation time.

**What it does NOT protect against:**
`llm.invoke()` failures — rate limits, timeouts, network errors.
These happen after the loop is done. The backup never gets a chance.

**Concrete example (our project — Groq free tier):**
You've made 30 requests this minute. Groq says "rate limit exceeded."
That error comes from `llm.invoke()`, not `ChatGroq()`.
Loop is already finished. Backup model never runs. Program crashes.

**Your answer:**
The loop protects against invalid model names — if `ChatGroq()` raises, the backup kicks in.
It does NOT protect against `llm.invoke()` failures like rate limits or timeouts —
that line is outside the loop, so the backup never runs.

**The fix (if asked in interview):**
Wrap `llm.invoke()` in its own try/except loop that retries with the backup model.

---

## Core Architecture Mental Model

```
Agent  = pure worker. Takes data, returns data. No state awareness.
Node   = bridge. Reads from state → calls agent → writes back to state.
State  = shared notebook. Every node reads and writes to same dict.
Builder = assembler. Wires nodes together with edges.
Graph  = compiled pipeline. Takes initial_state, runs nodes in order.
```

**The 3-variable connection:**
```
ContextFlowState (TypedDict)  → the SCHEMA. Blueprint. Read at compile time.
StateGraph(ContextFlowState)  → the GRAPH OBJECT. Knows schema + wiring.
initial_state (dict)          → runtime DATA. Flows through graph. Must match schema.
```

LangGraph validates `initial_state` against `ContextFlowState` on first invoke.
Each node returns a partial dict. LangGraph merges it into current state.
Unknown keys → rejected. Missing required keys → error before first node runs.

---

## Patterns Extracted

| Pattern | Rule |
|---------|------|
| P-014 | Agent = pure worker. Node = bridge. Never mix. |
| P-015 | State carries data between nodes. Nodes never call each other directly. |
| P-016 | Conditional edges replace if/else loops. Routing function returns string → map resolves to node. |
| P-017 | Fallback chains wrap initialization, not invocation. Protect both separately. |
