# Day 1 — Complete Understanding (My POV)

**Date:** Week 1, Day 1  
**What I Learned:** State management, execution flow, TypedDict vs initial_state, how everything connects

---

## 🎯 THE BIG PICTURE (What I Understood)

When I run `python src/main.py`, the whole system starts. It loads environment variables so that the Observer and Guide agents can access the Groq API key later. Then it asks me what I'm trying to learn, builds the graph, and runs everything automatically.

The key thing I understood: **There are 3 different "states" and they're NOT the same thing.**

---

## 📚 THE 3 STATES (This Was Confusing, Now Clear!)

### **1. ContextFlowState (TypedDict) — The Blueprint**

**CODE (src/graph/state.py):**
```python
from typing import TypedDict

class ContextFlowState(TypedDict):
    screenshot_b64: str
    capture_timestamp: str
    user_intent: str
    session_history: list
    extracted_context: dict
    guidance: dict
    error: str | None
    loop_count: int
    should_continue: bool
```

**WHAT IS IT?**
- A **type definition** (not a variable with data)
- Just a **blueprint** or **schema**
- Says: "State must have these 9 fields with these types"
- **NEVER gets updated** (it's just a template)

**ANALOGY:**
- Like a blank form template (PDF file)
- Has boxes labeled "Name:", "Age:", "Email:"
- No actual data, just structure
- You never write on the template itself

**WHY WE NEED IT:**
1. **Type safety** — If I misspell `state["screenshott_b64"]`, my IDE warns me
2. **Validation** — LangGraph checks if state matches this schema
3. **Autocomplete** — When I type `state["`, IDE shows all valid keys

---

### **2. StateGraph (LangGraph Class) — The Graph Builder**

**CODE (src/graph/builder.py, line 113):**
```python
from langgraph.graph import StateGraph

graph = StateGraph(ContextFlowState)
```

**WHAT IS IT?**
- A **class** from LangGraph library
- Used to **build** the execution graph
- Takes `ContextFlowState` as parameter (tells it the state structure)

**ANALOGY:**
- Like a race track builder (construction company)
- You give it the notebook format (ContextFlowState)
- It builds the race track with that format in mind

**WHAT IT DOES:**
```python
graph = StateGraph(ContextFlowState)  # Create builder

# Add nodes (runners)
graph.add_node("capture", capture_node)
graph.add_node("observer", observer_node)
graph.add_node("guide", guide_node)
graph.add_node("output", output_node)

# Add edges (automatic paths)
graph.add_edge("capture", "observer")  # Always go capture → observer
graph.add_edge("guide", "output")      # Always go guide → output

# Add conditional edges (decision points)
graph.add_conditional_edges(
    "observer",
    should_retry_capture,  # Routing function
    {
        "guide": "guide",      # If confidence >= 0.6 → go to guide
        "capture": "capture",  # If confidence < 0.6 → retry capture
        END: END,              # If error → exit
    }
)

# Set entry point (where to start)
graph.set_entry_point("capture")

# Compile (build the actual graph)
app = graph.compile()
```

**KEY POINT:** `StateGraph` is a **tool for building**. It's not the state itself, it's the builder that uses the state schema.

---

### **3. initial_state (Python Dictionary) — The Actual Data**

**CODE (src/main.py, lines 49-59):**
```python
initial_state = {
    "screenshot_b64": "",
    "capture_timestamp": "",
    "user_intent": "Learn Python",  # From user input
    "session_history": [],
    "extracted_context": {},
    "guidance": {},
    "error": None,
    "loop_count": 0,
    "should_continue": True,
}
```

**WHAT IS IT?**
- A **regular Python dictionary** (actual data)
- Contains **actual values** (empty strings, zero, user input)
- This is what gets passed to nodes and updated

**ANALOGY:**
- Like a filled-out form (actual paper with data)
- "Name: Sathvik", "Age: 21", "Email: sathvik@example.com"
- This is the actual notebook with data

**WHAT HAPPENS TO IT:**
- Gets passed to `app.invoke(initial_state)`
- Nodes read from it: `screenshot_b64 = state.get("screenshot_b64")`
- Nodes write to it: `return {"screenshot_b64": "iVBORw0..."}`
- LangGraph merges updates into it
- **This is the ONLY thing that gets updated**

---

## 🔄 HOW THEY WORK TOGETHER

```
ContextFlowState (Blueprint)
    ↓ (Used by)
StateGraph (Builder)
    ↓ (Validates)
initial_state (Actual Data)
```

**STEP 1:** Define schema (state.py)
```python
class ContextFlowState(TypedDict):
    screenshot_b64: str
    loop_count: int
```
**ROLE:** Blueprint (defines structure)

**STEP 2:** Create graph builder (builder.py)
```python
graph = StateGraph(ContextFlowState)  # Pass schema to builder
```
**ROLE:** Builder (uses schema to validate)

**STEP 3:** Create actual data (main.py)
```python
initial_state = {
    "screenshot_b64": "",
    "loop_count": 0
}
```
**ROLE:** Actual data (matches schema)

**STEP 4:** Run graph (main.py)
```python
result = app.invoke(initial_state)
```
**ROLE:** Execute graph with actual data

---

## 🚀 COMPLETE EXECUTION FLOW (When I Run `python src/main.py`)

### **STEP 1: Load Environment Variables (main.py, line 13)**

**CODE:**
```python
from dotenv import load_dotenv
load_dotenv()
```

**WHAT HAPPENS:**
- Reads `.env` file
- Loads `GROQ_API_KEY` into `os.environ`
- Now observer.py and guide.py can access it later with `os.getenv("GROQ_API_KEY")`

**ANALOGY:** Unlocking the house before entering. The API key is the key.

---

### **STEP 2: Ask User Intent (main.py, lines 33-40)**

**CODE:**
```python
user_intent = input("What are you trying to learn? → ").strip()
if not user_intent:
    user_intent = "general learning"
```

**WHAT HAPPENS:**
- I type: "Learn Python"
- Stored in `user_intent` variable
- This gets passed to Observer and Guide agents

---

### **STEP 3: Build Graph (main.py, line 45)**

**CODE:**
```python
app = build_graph()
```

**WHAT HAPPENS:**
- Calls `build_graph()` function from builder.py
- Returns a compiled LangGraph app
- This app is the "traffic controller"

**INSIDE build_graph() (builder.py):**

**Line 113: Create StateGraph**
```python
graph = StateGraph(ContextFlowState)
```
- `graph` = variable holding the graph object
- `StateGraph` = LangGraph class (blueprint maker)
- `ContextFlowState` = our schema (the blank form)
- LangGraph stores: "State dicts must have these 9 fields"

**Lines 117-120: Add Nodes**
```python
graph.add_node("capture", capture_node)
graph.add_node("observer", observer_node)
graph.add_node("guide", guide_node)
graph.add_node("output", output_node)
```
- Registers 4 nodes (the workers)
- Each node has a name ("capture") and a function (capture_node)

**Lines 124-125: Add Edges (Automatic Routing)**
```python
graph.add_edge("capture", "observer")
graph.add_edge("guide", "output")
```
- After capture → ALWAYS go to observer
- After guide → ALWAYS go to output

**Lines 131-142: Add Conditional Edges (Decision Points)**
```python
graph.add_conditional_edges(
    "observer",
    should_retry_capture,
    {
        "guide": "guide",
        "capture": "capture",
        END: END,
    }
)
```
- After observer → call `should_retry_capture(state)`
- If returns "guide" → go to guide_node
- If returns "capture" → go back to capture_node (retry)
- If returns END → exit graph

**Line 165: Set Entry Point**
```python
graph.set_entry_point("capture")
```
- Tells LangGraph: "Start here when app.invoke() is called"

**Line 168: Compile Graph**
```python
app = graph.compile()
```
- Validates graph structure (no broken edges)
- Converts blueprint → runnable app
- Returns compiled app with `.invoke()` method

---

### **STEP 4: Create Initial State (main.py, lines 49-59)**

**CODE:**
```python
initial_state = {
    "screenshot_b64": "",
    "capture_timestamp": "",
    "user_intent": "Learn Python",
    "session_history": [],
    "extracted_context": {},
    "guidance": {},
    "error": None,
    "loop_count": 0,
    "should_continue": True,
}
```

**WHAT HAPPENS:**
- Creates dict with **default values**
- `screenshot_b64 = ""` (empty string, not None)
- `loop_count = 0` (zero, not empty)
- `user_intent = "Learn Python"` (from my input)
- Matches `ContextFlowState` schema

---

### **STEP 5: Run Graph (main.py, line 67)**

**CODE:**
```python
result = app.invoke(initial_state)
```

**WHAT HAPPENS (The Big One!):**

```
1. LangGraph receives initial_state (the actual dict)

2. Validates: Does initial_state match ContextFlowState schema?
   - Has "screenshot_b64" key? ✅
   - Is it a string? ✅
   - Has "loop_count" key? ✅
   - Is it an int? ✅
   (checks all 9 fields)

3. Looks up entry point: "capture"

4. Calls capture_node(initial_state)

5. capture_node does:
   - Calls capture_screen() from capture/screen.py
   - mss grabs screenshot → raw pixels
   - PIL resizes to 1280x800
   - base64 encodes → string
   - Returns: {"screenshot_b64": "iVBORw0...", "capture_timestamp": "..."}

6. LangGraph MERGES return dict into initial_state:
   initial_state["screenshot_b64"] = "iVBORw0..."
   initial_state["capture_timestamp"] = "..."

7. Validates again: Does updated state still match schema? ✅

8. Looks up next node: "observer" (from add_edge)

9. Calls observer_node(initial_state)  # Now has screenshot

10. observer_node does:
    - Reads screenshot_b64 from state
    - Calls run_observer() from agents/observer.py
    - Sends to Groq Vision API (Llama 4 Scout)
    - API decodes base64 → sees actual image
    - Returns JSON: {"content_type": "code", "confidence": 0.85, ...}
    - Returns: {"extracted_context": {...}}

11. LangGraph MERGES into initial_state:
    initial_state["extracted_context"] = {...}

12. Looks up conditional edge: should_retry_capture(initial_state)

13. should_retry_capture checks:
    confidence = state["extracted_context"]["confidence"]
    if confidence >= 0.6:
        return "guide"
    else:
        return "capture"

14. Returns "guide" (confidence is 0.85)

15. LangGraph routes to guide_node

16. Calls guide_node(initial_state)

17. guide_node does:
    - Reads extracted_context from state
    - Calls run_guide() from agents/guide.py
    - Sends to Groq Text API (Llama 3.3 70B)
    - Returns: {"guidance": {...}}

18. LangGraph MERGES into initial_state:
    initial_state["guidance"] = {...}

19. Looks up next node: "output" (from add_edge)

20. Calls output_node(initial_state)

21. output_node does:
    - Reads guidance from state
    - Displays to CLI using rich library
    - Copies context_package to clipboard (pbcopy)
    - Asks: "Continue or Quit?"
    - I press "q" (quit)
    - Returns: {"loop_count": 1, "should_continue": False}

22. LangGraph MERGES into initial_state:
    initial_state["loop_count"] = 1
    initial_state["should_continue"] = False

23. Looks up conditional edge: should_continue_loop(initial_state)

24. should_continue_loop checks:
    if state["should_continue"]:
        return "capture"
    else:
        return END

25. Returns END (should_continue is False)

26. LangGraph exits, returns final initial_state
```

**KEY INSIGHT:** LangGraph automatically:
- Calls nodes in order
- Merges return dicts into state
- Routes based on conditional edges
- Handles loops
- Exits when reaching END

---

### **STEP 6: Print Summary (main.py, lines 70-78)**

**CODE:**
```python
if result.get("error"):
    console.print(f"⚠️  Error occurred: {result.get('error')}", style="red")

console.print("✅ ContextFlow session complete!", style="bold green")
console.print(f"   Total captures: {result.get('loop_count', 0)}", style="green")
```

**WHAT HAPPENS:**
- main.py receives `result` (the final state)
- Prints: "Session complete! Total captures: 1"

---

## 📊 FLOWCHART (Visual Flow)

```
USER RUNS: python src/main.py
    ↓
main.py: load_dotenv()
    ↓
main.py: user_intent = input("What are you learning?")
    ↓
main.py: app = build_graph()
    ↓
builder.py: graph = StateGraph(ContextFlowState)
    ↓
builder.py: graph.add_node("capture", capture_node)
builder.py: graph.add_node("observer", observer_node)
builder.py: graph.add_node("guide", guide_node)
builder.py: graph.add_node("output", output_node)
    ↓
builder.py: graph.add_edge("capture", "observer")
builder.py: graph.add_edge("guide", "output")
    ↓
builder.py: graph.add_conditional_edges(...)
    ↓
builder.py: graph.set_entry_point("capture")
    ↓
builder.py: app = graph.compile()
    ↓
main.py: initial_state = {...}
    ↓
main.py: result = app.invoke(initial_state)
    ↓
LangGraph: Validates initial_state matches schema ✅
    ↓
LangGraph: Calls capture_node(initial_state)
    ↓
capture_node → capture/screen.py → mss + PIL + base64
    ↓
Returns: {"screenshot_b64": "...", "timestamp": "..."}
    ↓
LangGraph: Merges into initial_state
    ↓
LangGraph: Calls observer_node(initial_state)
    ↓
observer_node → agents/observer.py → Groq Vision API
    ↓
Returns: {"extracted_context": {...}}
    ↓
LangGraph: Merges into initial_state
    ↓
LangGraph: Calls should_retry_capture(initial_state)
    ↓
Checks: confidence >= 0.6? → YES
    ↓
Returns: "guide"
    ↓
LangGraph: Routes to guide_node
    ↓
guide_node → agents/guide.py → Groq Text API
    ↓
Returns: {"guidance": {...}}
    ↓
LangGraph: Merges into initial_state
    ↓
LangGraph: Calls output_node(initial_state)
    ↓
output_node → output/cli.py → rich display + pbcopy
    ↓
Returns: {"loop_count": 1, "should_continue": False}
    ↓
LangGraph: Merges into initial_state
    ↓
LangGraph: Calls should_continue_loop(initial_state)
    ↓
Checks: should_continue == True? → NO
    ↓
Returns: END
    ↓
LangGraph: Exits, returns final state
    ↓
main.py: Prints "Session complete! Total captures: 1"
```

---

## 🗂️ FILE RESPONSIBILITIES (Where Does Code Live?)

### **LAYER 1: Entry Point**
- **src/main.py** — Loads env, asks user intent, calls build_graph(), runs app.invoke()

### **LAYER 2: Orchestration**
- **src/graph/builder.py** — Assembles StateGraph, defines edges, compiles
- **src/graph/state.py** — Defines ContextFlowState schema (TypedDict)
- **src/graph/nodes.py** — Wrapper functions (read state → call agent → write state)

### **LAYER 3: Business Logic**
- **src/agents/observer.py** — Vision AI (Groq API, JSON validation)
- **src/agents/guide.py** — Text AI (Groq API, prompt selection)
- **src/capture/screen.py** — mss screenshot, PIL resize, base64 encode
- **src/output/cli.py** — rich display, pbcopy clipboard

---

## 🧩 HOW FILES COMMUNICATE (Import Chain)

**main.py imports:**
```python
from dotenv import load_dotenv
from src.graph.builder import build_graph
from rich.console import Console
```

**builder.py imports:**
```python
from langgraph.graph import StateGraph, END
from src.graph.state import ContextFlowState
from src.graph.nodes import capture_node, observer_node, guide_node, output_node
```

**nodes.py imports:**
```python
from src.agents.guide import run_guide
from src.agents.observer import run_observer
from src.capture.screen import capture_screen
from src.graph.state import ContextFlowState
from src.output.cli import copy_to_clipboard, display_guidance, prompt_continue
```

**KEY POINT:** Clean dependency chain. No circular imports.

---

## 🎯 KEY CONCEPTS (What I Mastered)

### **1. TypedDict vs initial_state**
- **TypedDict** = Blueprint (no data, just structure)
- **initial_state** = Actual data (gets updated)
- LangGraph uses TypedDict for validation, updates initial_state

### **2. StateGraph vs State**
- **StateGraph** = Builder tool (creates graph)
- **State** = Data dictionary (flows through graph)

### **3. Nodes vs Agents**
- **Nodes** = Wrappers (read state → call agent → write state)
- **Agents** = Workers (business logic, API calls)

### **4. Edges vs Conditional Edges**
- **Edges** = Automatic routing (always go A → B)
- **Conditional Edges** = Decision points (check state, route accordingly)

### **5. How LangGraph Merges Updates**
- Nodes return dicts: `{"screenshot_b64": "..."}`
- LangGraph merges: `state["screenshot_b64"] = "..."`
- Automatic, no manual merge code needed

---

## ✅ WHAT I CAN DO NOW

- ✅ Explain complete execution flow (main.py → builder.py → nodes → agents)
- ✅ Understand TypedDict vs initial_state (schema vs data)
- ✅ Know where each piece of code lives (file mapping)
- ✅ Trace how state updates (nodes return dicts, LangGraph merges)
- ✅ Understand conditional edges (routing logic)
- ✅ Add a new agent (know which files to modify)

---

## 🎤 INTERVIEW ANSWERS (Polished)

**Q: "Walk me through what happens when you run main.py"**

> "When I run main.py, it first loads environment variables so Observer and Guide can access the Groq API key. Then it asks what I'm learning, calls build_graph() from builder.py which creates a StateGraph with 4 nodes and conditional edges, compiles it, and returns a runnable app. Then it creates initial_state with default values, calls app.invoke(initial_state), and LangGraph orchestrates the entire flow—calling nodes, merging updates, routing based on conditional edges—until it reaches END. Finally, main.py prints a summary."

**Q: "What's the difference between ContextFlowState and initial_state?"**

> "ContextFlowState is a TypedDict—just a schema that defines structure. It has no data, never gets updated. initial_state is an actual Python dictionary with real values that flows through the graph and gets updated by nodes. LangGraph uses ContextFlowState for validation and type safety, but only initial_state holds actual data."

**Q: "How do nodes communicate?"**

> "Nodes communicate through shared state. Each node reads from state, does work, and returns a dict with updates. LangGraph automatically merges that dict into state. For example, capture_node returns {"screenshot_b64": "..."}, LangGraph merges it, then observer_node reads that screenshot from state. It's like a relay race notebook—each runner reads it, writes in it, passes it on."

---

**END OF DAY 1 UNDERSTANDING**

Next: Day 2 — Observer Agent, Guide Agent, LangGraph Patterns
