# ContextFlow — Master Learning Notes
**Auto-updated after every task | Your interview prep reference**

Last Updated: Day 3 Complete (May 10, 2026, 9:46 PM)  
Progress: 9/34 tasks (26%) — Week 1 COMPLETE

---

## 🎯 PROJECT VISION

**Problem:** Developers waste 30-100 min/day manually gathering context (screenshots, copy-paste, typing explanations) to share with LLMs.

**Solution:** One hotkey → AI agents automatically gather context from 6 sources → clipboard → paste into any LLM.

**Goal:** 3-5 minutes → 2 seconds. Zero manual work.

---

## 🧠 CORE CONCEPTS (Memorize These)

### 0. THE RELAY RACE ANALOGY (Explain This to Anyone)

**Imagine 4 runners in a relay race:**
1. **Runner 1 (Capture):** Takes a photo with a camera
2. **Runner 2 (Observer):** Looks at the photo and writes notes
3. **Runner 3 (Guide):** Reads the notes and gives advice
4. **Runner 4 (Output):** Shows the advice on a big screen

**The Notebook = State**

Instead of passing a baton, they pass a **notebook**. Each runner:
- Reads what previous runners wrote
- Adds their own notes
- Passes the notebook to the next runner

**WITHOUT LangGraph (Manual):**
You stand there and tell each runner: "Runner 1, go! Now Runner 2, go! Now Runner 3, go!"

**WITH LangGraph (Automatic):**
The runners know the order automatically. You just say "START!" and they run in sequence without you telling each one.

**Conditional Edges (Smart Routing):**
Runner 2 (Observer) checks the photo quality:
- If photo is clear → pass notebook to Runner 3 (Guide)
- If photo is blurry → pass notebook back to Runner 1 (Capture) to retake photo

**Interview Answer:** "State is like a notebook passed between runners in a relay race. Each agent reads what it needs and writes its results. LangGraph orchestrates the flow automatically, with conditional edges making smart routing decisions based on the data."

---

### 1. STATE MANAGEMENT (The Relay Race Baton)
```python
class ContextFlowState(TypedDict):
    screenshot_b64: str          # Capture fills this
    extracted_context: dict      # Observer fills this
    guidance: dict               # Guide fills this
    error: Optional[str]         # Error node fills this
    loop_count: int              # Tracks iterations
    should_continue: bool        # Controls loop exit
```

**Analogy:** State is the baton in a relay race. Each agent (runner) receives it, adds their data, and passes it to the next agent.

**Why TypedDict?** Type safety + autocomplete + validation at compile time.

**Interview Question:** "How do agents communicate in your system?"  
**Answer:** "Through a shared TypedDict state that gets passed from node to node. Each agent reads what it needs and writes its output back to the state."

---

### 2. LANGGRAPH ORCHESTRATION (The Factory Assembly Line)

**WITHOUT LangGraph:**
```python
# Manual orchestration — you control everything
screenshot = capture_screen()
context = run_observer(screenshot)
guidance = run_guide(context)
display_guidance(guidance)
```

**WITH LangGraph:**
```python
# Automatic orchestration — graph controls flow
graph = StateGraph(ContextFlowState)
graph.add_node("capture", capture_node)
graph.add_node("observer", observer_node)
graph.add_edge("capture", "observer")  # Automatic routing
app = graph.compile()
result = app.invoke(initial_state)  # Runs entire flow
```

**Key Benefits:**
1. **Automatic flow** — Nodes call each other
2. **Error handling** — Routes to error_node on failure
3. **Conditional routing** — "If X, go to Y" logic
4. **Retry logic** — Re-capture if confidence low
5. **Scalability** — Add new agents = add new nodes

**Analogy:** Factory assembly line. Each station knows its job, passes work automatically, routes to quality control if something breaks.

**Interview Question:** "Why use LangGraph instead of manual function calls?"  
**Answer:** "LangGraph provides automatic orchestration, error handling, conditional routing, and retry logic. It's like moving from manual assembly to an automated factory line."

---

### 3. MULTI-AGENT PATTERN (Separation of Concerns)

**Observer Agent (Vision):**
- **Job:** Turn pixels → structured JSON
- **Model:** Llama 4 Scout Vision
- **Input:** base64 PNG screenshot
- **Output:** `{content_type, title, primary_text, code_blocks, error_messages, url_visible, confidence}`

**Guide Agent (Text Reasoning):**
- **Job:** Turn observations → actionable advice
- **Model:** Llama 3.3 70B (text, NOT vision)
- **Input:** Observer's JSON output
- **Output:** `{summary, learning_path, questions_to_ask, context_package}`

**Why 2 agents, not 1?**
1. **Specialization** — Vision models are bad at reasoning, text models are bad at vision
2. **Cost** — Vision API calls are expensive, text is cheap
3. **Modularity** — Can swap models independently
4. **Debugging** — Easier to debug 2 focused agents than 1 complex agent

**Interview Question:** "Why not use one agent for everything?"  
**Answer:** "Separation of concerns. Vision models excel at extracting content, text models excel at reasoning. Using both gives better results and lower cost."

---

## 📦 WHAT GETS COPIED TO CLIPBOARD

```
=== ContextFlow Snapshot — 2026-05-10 13:15:42 ===
CONTENT TYPE: youtube
TITLE: React Hooks Tutorial
URL: https://www.youtube.com/watch?v=abc123

WHAT'S ON SCREEN:
[Primary text extracted by Observer]

CODE VISIBLE:
[Code blocks extracted by Observer]

ERRORS DETECTED:
[Error messages extracted by Observer]

SUGGESTED QUESTIONS FOR LLMs:
1. [Question generated by Guide]
2. [Question generated by Guide]

=== END SNAPSHOT ===
```

**Why this format?**
- Structured for LLMs to parse instantly
- No manual typing needed
- Complete context in one paste

---

## 🔄 DATA FLOW (Current State - Day 2)

```
1. capture_screen() 
   → screenshot_b64 (base64 PNG)

2. run_observer(screenshot_b64)
   → extracted_context (JSON with 7 fields)

3. run_guide(extracted_context)
   → guidance (summary, learning_path, questions, context_package)

4. display_guidance(guidance)
   → rich CLI output (colored panels)

5. copy_to_clipboard(context_package)
   → macOS clipboard (pbcopy)
```

**What's Missing:** No automatic orchestration, no error handling, no retry logic, no loop control.

**That's what TASK-007 adds.**

---

## 🛠️ TECH STACK DECISIONS

| Technology | Why This Choice |
|------------|----------------|
| **Python 3.11** | Mature, great AI libraries, type hints |
| **LangGraph** | Best multi-agent orchestration framework |
| **Groq API** | Free tier, fast inference, Llama models |
| **Llama 4 Scout Vision** | Free, good accuracy, handles screenshots |
| **Llama 3.3 70B** | Free, excellent reasoning, fast |
| **mss** | Fastest screenshot library (10x faster than PIL) |
| **Pillow** | Image processing (resize, encode) |
| **rich** | Beautiful CLI output (colored panels) |
| **pynput** | Hotkey listener (Week 4) |
| **uv** | 10-100x faster than pip |

---

## 🎓 TASKS COMPLETED (Days 1-2)

### ✅ TASK-001: Project Scaffold
**What:** Created folder structure, `pyproject.toml`, `.env`, `.gitignore`  
**Why:** Professional Python project setup  
**Key Learning:** `uv` package manager is 10-100x faster than `pip`

### ✅ TASK-002: State Schema
**What:** Created `ContextFlowState` TypedDict in `src/graph/state.py`  
**Why:** Shared memory between agents (the relay race baton)  
**Key Learning:** TypedDict provides type safety without runtime overhead

**2 Lines to Memorize:**
```python
class ContextFlowState(TypedDict):
    screenshot_b64: str  # The baton passed between agents
```

### ✅ TASK-003: Screen Capture
**What:** Created `capture_screen()` in `src/capture/screen.py`  
**Why:** Convert screen pixels → base64 PNG for Vision API  
**Key Learning:** mss is 10x faster than PIL for screenshots

**2 Lines to Memorize:**
```python
with mss.mss() as sct:
    screenshot = sct.grab(monitor)  # Fastest screenshot method
```

### ✅ TASK-004: Observer Agent
**What:** Created `run_observer()` in `src/agents/observer.py`  
**Why:** Turn pixels → structured JSON (content_type, title, code, errors)  
**Key Learning:** Vision models return markdown fences, must strip them

**Technical Challenge Solved:** Groq deprecated Llama 3.2 Vision mid-development → migrated to Llama 4 Scout in 30 minutes

**2 Lines to Memorize:**
```python
cleaned = re.sub(r"^```(?:json)?\s*\n?", "", raw_content.strip())
# Never trust LLM output format — always clean and validate
```

### ✅ TASK-005: Guide Agent
**What:** Created `run_guide()` in `src/agents/guide.py`  
**Why:** Turn observations → actionable advice (summary, learning path, questions)  
**Key Learning:** Content-type-specific prompts (YouTube vs docs vs code vs errors)

**2 Lines to Memorize:**
```python
prompt_template = GUIDE_PROMPTS[content_type]
# Different content types need different advice strategies
```

### ✅ TASK-006: Output Node
**What:** Created `display_guidance()` in `src/output/cli.py`  
**Why:** Beautiful terminal display + clipboard integration  
**Key Learning:** rich library makes CLI output professional

**2 Lines to Memorize:**
```python
console.print(Panel(summary, title="Summary", style="bold green"))
# Professional CLI output matters for user experience
```

### ✅ TASK-007: LangGraph Assembly
**What:** Created `build_graph()` in `src/graph/builder.py`  
**Why:** Automatic orchestration with conditional routing and error handling  
**Key Learning:** LangGraph separates routing logic from business logic

**The Graph Structure:**
```
START → capture → observer → [confidence check] → guide → output → [continue check] → END
                     ↓                                        ↓
                [if confidence < 0.6]                  [if should_continue]
                     ↓                                        ↓
                  capture ←────────────────────────────────────┘
```

**Conditional Edges:**
1. **After observer:** Check confidence >= 0.6?
   - YES → go to guide (continue)
   - NO → go to capture (retry)

2. **After output:** Check should_continue?
   - YES → go to capture (loop)
   - NO → go to END (exit)

**Why Conditional Edges > If/Else in Nodes:**
- **Separation of concerns:** Observer extracts, graph routes
- **Modularity:** Can change routing without touching node code
- **Testability:** Can test routing logic separately
- **Visibility:** Graph structure is declarative and clear

**2 Lines to Memorize:**
```python
graph.add_conditional_edges("observer", should_retry_capture, {"guide": "guide", "capture": "capture"})
# Conditional edges separate routing logic from business logic — key LangGraph pattern
```

---

### ✅ TASK-008: Entry Point
**What:** Created `src/main.py` as user-facing entry point  
**Why:** Single command to run the full system with user intent prompt  
**Key Learning:** User intent personalizes guidance — same screen, different advice

**2 Lines to Memorize:**
```python
user_intent = input("   → ").strip()
# User intent drives personalized guidance — key to useful AI assistants
```

### ✅ TASK-009: Integration Test
**What:** Created `tests/test_integration.py` with 3 tests  
**Why:** Validate Milestone 2 complete — full loop working  
**Key Learning:** Integration tests reveal bugs unit tests miss

**Technical Challenge Solved:** Infinite loop bug — Observer failed + low confidence → retry forever. Fixed with error check in conditional edge.

**2 Lines to Memorize:**
```python
if state.get("error"):
    return "END"  # Exit on error — prevents infinite retry loops
```

### ✅ DAY 3 FIX: Observer Priority Rule
**What:** Added PRIORITY RULE to Observer prompt to prioritize browser content over terminal  
**Why:** When both browser and terminal visible, Observer was analyzing terminal code instead of browser content  
**Key Learning:** Prompt engineering is critical for multi-window scenarios

**The Problem:**
- User opens ESPN cricket page + terminal with Python code
- Observer analyzes terminal (Python code) instead of browser (cricket content)
- Can't prove ContextFlow works on ANY content (sports, not just tech)

**The Solution:**
Added explicit instruction to Observer prompt:
```
PRIORITY RULE (MOST IMPORTANT):
If the screenshot shows BOTH a browser/application window AND a terminal/IDE:
→ ANALYZE THE BROWSER/APPLICATION CONTENT, NOT THE TERMINAL
→ Ignore terminal windows, code editors, and development tools
→ Focus on the MAIN CONTENT the user is viewing
```

**Result:** Observer now correctly analyzes ESPN cricket content even with terminal visible ✅

**2 Lines to Memorize:**
```python
# Observer prompt: "If browser + terminal visible → analyze browser, ignore terminal"
# Prompt engineering solves multi-window priority without code changes
```

**Future Enhancement (Week 2+):**
Pass `user_intent` to Observer to dynamically decide priority:
- Intent: "Explain this cricket match" → Prioritize browser
- Intent: "Debug this Python error" → Prioritize terminal

---

## 🚀 NEXT: Week 2 — File Reader + Terminal Watcher (Days 4-7)

---

## 🎯 LANGGRAPH PATTERNS (Universal — Apply to Any Project)

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

### Pattern 2: Conditional Edge
```python
def should_retry(state: MyState) -> str:
    """Routing function returns next node name."""
    if state["confidence"] < 0.6:
        return "capture"  # Re-capture
    else:
        return "guide"    # Continue
```

### Pattern 3: Error Handling
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

**These patterns work for ANY LangGraph project.**

---

## 📝 INTERVIEW PREP — KEY TALKING POINTS

### "Tell me about your ContextFlow project"
"I built a multi-agent system that automates context gathering for LLMs. It uses LangGraph to orchestrate two specialized agents: Observer (vision) extracts content from screenshots, Guide (text reasoning) generates actionable advice. The system reduces manual workflow from 3-5 minutes to 2 seconds with one hotkey. I solved challenges like model deprecation mid-development and non-deterministic LLM output parsing."

### "How do your agents communicate?"
"Through a shared TypedDict state that acts like a relay race baton. Each agent receives the state, reads what it needs, adds its output, and passes it to the next agent. LangGraph handles the orchestration automatically."

### "Why use multiple agents instead of one?"
"Separation of concerns. Vision models excel at extracting content but are bad at reasoning. Text models excel at reasoning but can't process images. Using both gives better results and lower cost. It's also more modular — I can swap models independently."

### "What was your biggest technical challenge?"
"Groq deprecated Llama 3.2 Vision models mid-development. I had to migrate to Llama 4 Scout in 30 minutes with zero downtime. I built resilient API integration with fallback logic and strict schema validation to handle non-deterministic LLM outputs."

---

## 🔄 AUTO-UPDATE RULES

This file auto-updates after every task with:
1. ✅ New task summary (what, why, key learning)
2. ✅ 2 lines to memorize from the task
3. ✅ Technical challenges solved
4. ✅ New LangGraph patterns learned
5. ✅ Updated progress tracking

**Commit message:** `docs: update learning notes — TASK-XXX complete`

---

=== END LEARNING NOTES ===


---

## 📅 DAY 3 COMPLETE — User Intent Prompt (Personalization)

**Date:** May 12, 2026  
**Task:** Add user intent prompt to personalize guidance  
**Status:** ✅ Complete (with 4 hours of debugging)

### WHAT WE BUILT
Added interactive user intent prompt to `src/main.py`:
```python
user_intent = input("   → ").strip()
if not user_intent:
    user_intent = "general learning"
```

User is now asked: "📝 What are you trying to learn right now?"

Their answer gets passed to all agents via initial state:
```python
initial_state = {
    "user_intent": user_intent,  # ⭐ NEW! Day 3 addition
    ...
}
```

### WHY IT MATTERS
**Day 2:** Generic advice for everyone (not useful)  
**Day 3:** Personalized advice based on user's goal (actually helpful)

**Example:**
- Screen: ESPN cricket page
- Intent: "Explain this cricket match" → Guide gives cricket analysis
- Intent: "Build a sports website" → Guide gives web dev advice

**Same screen, different advice.** This is the power of personalization.

### KEY CONCEPTS LEARNED

#### 1. **Function** (`def main():`)
A named block of code that does a specific job. Like a recipe with a name, ingredients (parameters), and instructions (code inside).

#### 2. **Input** (`input("→ ")`)
Pauses program, waits for user to type, returns what they typed as a string. Essential for interactive programs.

#### 3. **Dictionary** (`{"key": "value"}`)
Collection of key-value pairs. Like a notebook with labeled sections. Agents read/write specific sections by name.

#### 4. **F-string** (`f"Hello {name}"`)
String with variables inserted using `{variable}`. Cleaner than concatenation (`"Hello " + name`).

#### 5. **Import** (`from X import Y`)
Brings code from another file so you can use it. Enables code organization across multiple files.

### 2 LINES TO MEMORIZE
```python
user_intent = input("   → ").strip()
# Pauses program, waits for user input, cleans up spaces

"user_intent": user_intent,  # Passes user's goal to all agents
```

**Why these matter:** They're the bridge between user and AI. Without them, the system is generic. With them, it's personalized.

### TECHNICAL CHALLENGES SOLVED

#### Challenge 1: Python 3.14 Syntax Errors
**Problem:** Numbered lists in docstrings (`1.`, `2.`, `3.`) broke with `SyntaxError: invalid decimal literal`  
**Root Cause:** Python 3.14 parses `1.` as decimal number  
**Solution:** Changed to bullet points (`-` instead of `1.`)  
**Lesson:** Never use Python 3.14 for production. Use 3.11 or 3.12.

#### Challenge 2: Observer JSON Parsing Failures
**Problem:** Observer returning invalid JSON (`'\n  "content_type"'`)  
**Root Cause:** Prompt too complex (70 lines), vision model confused  
**Solution:** Simplified prompt from 70 lines → 30 lines  
**Lesson:** Vision models need SHORT prompts (<40 lines). Long prompts = confusion.

#### Challenge 3: Observer Analyzing Wrong Window
**Problem:** Observer analyzing terminal instead of browser (ESPN cricket)  
**Root Cause:** Terminal has clearer text, gets priority  
**Solution:** Added PRIORITY RULE to prompt: "If browser + terminal visible → analyze browser"  
**Lesson:** Prompt engineering can solve multi-window priority without code changes.

### DEBUGGING MARATHON (4 hours)
Day 3 was mostly debugging, not feature work. Spent 4 hours fixing:
1. Python 3.14 syntax errors
2. Observer JSON parsing failures
3. Virtual environment activation issues
4. Observer analyzing wrong window

**Key Insight:** I learned more from 4 hours of debugging than 2 days of smooth development.

**Debugging teaches:**
- How systems ACTUALLY work (not how you think they work)
- How to read error messages (they're usually right)
- How to simplify when stuck (remove complexity until it works)
- How to stay calm when everything breaks

### LANGGRAPH PATTERNS REINFORCED

#### Pattern: Initial State Setup
```python
initial_state = {
    "screenshot_b64": "",
    "user_intent": user_intent,  # User's goal
    "extracted_context": {},
    "guidance": {},
    "error": None,
    "loop_count": 0,
    "should_continue": True,
}

result = app.invoke(initial_state)  # Runs entire graph
```

**Key Learning:** Initial state is passed to first node, then flows through all nodes. Each node reads what it needs and writes its output.

### INTERVIEW TALKING POINTS

**"Tell me about a technical challenge you faced"**
"On Day 3, I spent 4 hours debugging. The Observer agent was returning invalid JSON because my prompt was too complex (70 lines). Vision models get confused with long prompts. I simplified it to 30 lines and it worked. This taught me that AI prompt engineering is as important as code quality."

**"How do you handle debugging?"**
"I read error messages carefully, test one change at a time, and simplify when stuck. On Day 3, I had 6 different errors. I fixed them incrementally, documented each one in a debug log, and learned more from those 4 hours than from 2 days of smooth development."

**"Why did you add user intent?"**
"Personalization. Same screen, different goals. If you're watching a cricket match, you might want sports analysis OR web development advice (how to build a sports site). User intent makes the guidance actually useful instead of generic."

### FILES CHANGED
- `src/main.py` — Added user intent prompt, confirmation message, graph building visibility

### WEEK 1 COMPLETE ✅
**9/9 tasks done:**
1. ✅ GitHub repo + project structure
2. ✅ State schema (TypedDict)
3. ✅ Screen capture (mss → base64)
4. ✅ Observer agent (vision → JSON)
5. ✅ Guide agent (reasoning → advice)
6. ✅ Output node (rich CLI + clipboard)
7. ✅ Error node (catches failures)
8. ✅ LangGraph assembly (conditional edges)
9. ✅ User intent prompt (personalization)

**Next:** Week 2 — File Reader + Terminal Watcher agents

---

=== END DAY 3 LEARNING NOTES ===
