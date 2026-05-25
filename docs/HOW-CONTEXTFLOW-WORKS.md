# HOW CONTEXTFLOW WORKS — Project Understanding Reference
# Read this when you open the project after a break.
# Purpose: explain your project to anyone, at any level, confidently.

---

## WHAT IS CONTEXTFLOW

ContextFlow is a dev companion. One hotkey — and it instantly knows everything about
what you're doing: what's on your screen, what's in your terminal, what you're building.
It assembles full context and gives you intelligent guidance without you explaining anything.

Inspired by Wispr Flow's seamless one-key trigger. Vision: beyond Jarvis —
not just reactive when you ask, but eventually proactive, persistent, and context-aware
across your entire dev session.

Current state: the core intelligence pipeline is built and working.
What's being added: hotkey trigger, session memory, overlay UI, async background capture.

---

## THE TECHNICAL EXPLANATION (for interviews)

"ContextFlow is a Python AI pipeline built with LangGraph.
When triggered, it captures your screen and terminal context simultaneously.
Two specialized agents process this: Observer (vision model) extracts structured data
from the screenshot — content type, code, errors, confidence score.
Guide (text model) takes that structured data and generates a summary,
learning path, and a context package you can paste into any LLM.
The whole pipeline runs through a shared state object that every step reads from
and writes back to. LangGraph handles the routing — retrying if confidence is low,
looping if you want another capture, exiting cleanly on errors."

---

## THE DATA FLOW (what happens when triggered)

```
You press hotkey
        ↓
   main.py starts
   asks: "what are you working on?" → stored as user_intent
        ↓
   build_graph() — assembles the pipeline once
        ↓
   app.invoke(initial_state) — pipeline starts
        ↓
┌─── capture_node ──────────────────────────────────────┐
│  mss grabs screen pixels                              │
│  PIL: BGRA → RGB → resize to 1280×800 (token saving) │
│  base64 encodes pixels → text string                  │
│  terminal.py reads shell history → last 20 commands  │
│  → writes: screenshot_b64, terminal_context to state  │
└───────────────────────────────────────────────────────┘
        ↓
┌─── observer_node ─────────────────────────────────────┐
│  reads: screenshot_b64 from state                     │
│  calls: run_observer() in src/agents/observer.py      │
│    → sends base64 image to Groq Vision API            │
│    → model "sees" screen, returns JSON string         │
│    → strip markdown fences → json.loads() → dict      │
│    → validates: all fields present, confidence 0–1    │
│  → writes: extracted_context to state                 │
│    {content_type, title, code_blocks, confidence...}  │
└───────────────────────────────────────────────────────┘
        ↓
   confidence >= 0.6?
   NO  → back to capture_node (retry)
   YES ↓
┌─── guide_node ────────────────────────────────────────┐
│  reads: extracted_context from state                  │
│  calls: run_guide() in src/agents/guide.py            │
│    → sends structured text to Groq Text API           │
│    → model reasons, returns advice                    │
│  → writes: guidance to state                          │
│    {summary, learning_path, questions, context_pkg}   │
└───────────────────────────────────────────────────────┘
        ↓
┌─── output_node ───────────────────────────────────────┐
│  rich library: prints formatted output to terminal    │
│  pbcopy: copies context_package to clipboard          │
│  asks: "Continue? y/n"                                │
│  → writes: should_continue, loop_count to state       │
└───────────────────────────────────────────────────────┘
        ↓
   should_continue = True?
   YES → back to capture_node (loop)
   NO  → END
```

---

## THE 5 FILES AND THEIR SINGLE JOB

| File | Job | One-line rule |
|------|-----|---------------|
| `src/main.py` | Trigger | Asks intent, starts graph. Nothing else. |
| `src/graph/state.py` | Shared notebook | TypedDict. Every step reads/writes here. |
| `src/agents/observer.py` | Vision worker | base64 in → structured dict out. Knows nothing about LangGraph. |
| `src/agents/guide.py` | Text worker | extracted_context in → guidance dict out. Knows nothing about LangGraph. |
| `src/graph/nodes.py` | Bridges | Read from state → call agent → write back. No logic. |
| `src/graph/builder.py` | Assembler | Wires nodes + edges. Runs once. |

---

## HOW STATE WORKS (the key mechanism)

State is a TypedDict (typed dictionary) that flows through every step.
No step talks to another step directly — only through state.

```python
# observer_node reads from state, calls agent, returns only what changed:
def observer_node(state: ContextFlowState) -> dict:
    screenshot = state["screenshot_b64"]          # READ
    result = run_observer(screenshot)             # WORK
    return {"extracted_context": result}          # WRITE (partial dict)

# LangGraph auto-merges that partial dict back into full state.
# Everything not mentioned stays unchanged.
```

ContextFlowState in `src/graph/state.py` is the CONTRACT.
Every field that exists in the pipeline is declared there.
If a node writes a field not in the contract → LangGraph raises an error immediately.

---

## WHY THESE DESIGN DECISIONS

**Two agents, not one**
Vision models see but reason poorly. Text models reason but can't see.
Separating them: better output, each independently swappable, easier to debug.

**LangGraph, not manual function calls**
Manual: you write if/else retry logic, loop control, error handling by hand.
LangGraph: you declare edges. Routing, retries, loops → handled automatically.
Adding a new branch = one line. Not rewriting the flow.

**TypedDict for state, not plain dict**
Plain dict typo: `state["extracted_contxt"]` → silently returns None → invisible bug.
TypedDict typo: IDE underlines it red immediately. Caught before runtime.

---

## WHAT'S COMING (the full vision)

```
NOW (built):      capture → observe → guide → clipboard
NEXT:             hotkey trigger (no manual Enter)
SOON:             floating overlay UI (like Wispr Flow)
LATER:            session memory (remembers past captures)
VISION:           proactive suggestions (notifies you before you ask)
                  async background capture (always watching)
                  local AI option (Ollama, fully offline)
                  multi-source context (screen + terminal + browser + files)
```

---

## QUICK ANSWER FOR ANYONE WHO ASKS

**Non-technical person:**
"It's like having a smart assistant watching your screen. You press one key,
it reads everything visible — your code, errors, what you're watching —
and gives you instant guidance. You paste it into ChatGPT and it already
knows your full context. No explaining needed."

**Technical person:**
"It's a LangGraph pipeline with two specialized agents — a vision model and a text model —
communicating through a shared TypedDict state. One-key trigger captures screen + terminal context,
Observer extracts structure from the screenshot, Guide generates actionable guidance,
result hits clipboard. Built for extensibility: session memory, async capture,
and overlay UI are next."
