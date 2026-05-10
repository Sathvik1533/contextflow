# architecture.md — ContextFlow Multi-Agent System

## What is LangGraph and Why Here

LangGraph = state machine for AI agents. Normal LangChain = linear pipeline (A→B→done). LangGraph = graph with cycles. You need cycles because: Observer captures screen → Guide responds → user acts → screen changes → Observer captures again. Loop never ends until user quits. That's a graph, not a pipeline.

**Node** = a function that reads state, does work, writes back to state.
**Edge** = rule that decides which node runs next.
**State** = shared memory dict every node reads and writes.

---

## State Schema

This is the single source of truth passed between all nodes.

```python
from typing import TypedDict, Optional, List
from datetime import datetime

class ContextFlowState(TypedDict):
    # --- Input ---
    screenshot_b64: str              # Raw base64 PNG from mss capture
    capture_timestamp: str           # ISO timestamp of capture

    # --- Observer Output ---
    extracted_context: dict          # Structured JSON from Gemini Vision
    # extracted_context shape:
    # {
    #   "content_type": "youtube" | "documentation" | "code" | "other",
    #   "title": str,
    #   "primary_text": str,         # Main readable content on screen
    #   "code_blocks": List[str],    # Any code visible
    #   "error_messages": List[str], # Any errors/stack traces
    #   "url_visible": str | None,
    #   "confidence": float          # 0-1, how sure Vision is
    # }

    # --- Guide Output ---
    guidance: dict                   # Pedagogical response from Guide agent
    # guidance shape:
    # {
    #   "summary": str,              # 2-3 sentence summary of what's on screen
    #   "learning_path": List[str],  # Step-by-step next actions for user
    #   "questions_to_ask": List[str], # Suggested follow-up questions for LLMs
    #   "context_package": str       # Full context blob ready to paste into ChatGPT/Claude
    # }

    # --- Control Flow ---
    error: Optional[str]             # Set if any node fails
    loop_count: int                  # How many capture cycles have run
    should_continue: bool            # False = exit graph
```

---

## Node Definitions

### Node 1: `capture_node`
**Does:** Fires mss, grabs monitor pixels, encodes to base64.
**Reads from state:** Nothing (entry point).
**Writes to state:** `screenshot_b64`, `capture_timestamp`.
**Why separate node:** Isolates hardware interaction. Testable without API calls.

### Node 2: `observer_node` (Agent A)
**Does:** Sends `screenshot_b64` to Gemini 2.0 Flash Vision. Extracts structured JSON matching `extracted_context` schema.
**Reads from state:** `screenshot_b64`.
**Writes to state:** `extracted_context`.
**Model:** `gemini-2.0-flash` with vision.
**Why structured JSON:** Guide node needs predictable input. Free-text from Vision = brittle.

### Node 3: `guide_node` (Agent B)
**Does:** Reads `extracted_context`, generates pedagogical response. Builds the "context package" — the copy-pasteable blob for external LLMs.
**Reads from state:** `extracted_context`.
**Writes to state:** `guidance`.
**Model:** `gemini-2.0-flash` (text only).
**Why separate from Observer:** Different prompts, different roles. Observer = "what is on screen." Guide = "what should user do next." Mixing = worse outputs from both.

### Node 4: `output_node`
**Does:** Prints/renders guidance to UI. Increments `loop_count`. Asks user: continue or quit.
**Reads from state:** `guidance`, `loop_count`.
**Writes to state:** `should_continue`.
**Why separate:** Decouples UI from AI logic. Swap CLI for Mac overlay without touching agents.

### Node 5: `error_node`
**Does:** Catches failures from any node. Logs error. Sets `should_continue = False` or retries.
**Why needed:** Free tier rate limits WILL hit. Need graceful fallback, not crash.

---

## Edge Logic

```
START
  ↓
capture_node
  ↓
observer_node
  ↓ (if extracted_context.confidence > 0.6)
guide_node ──────────────────────────────────────────────────────→ error_node
  ↓ (if confidence ≤ 0.6, re-capture)                                  ↓
  └──────────────────────────────────────→ capture_node         should_continue=False
  ↓                                                                     ↓
output_node                                                            END
  ↓
[conditional edge]
  ├── should_continue=True  → capture_node  (loop)
  └── should_continue=False → END
```

**Conditional edge code (pseudocode):**
```python
def should_loop(state: ContextFlowState) -> str:
    if state["error"]:
        return "error_node"
    if state["should_continue"]:
        return "capture_node"   # back to top
    return END
```

---

## Context Package Format

This is what gets handed to ChatGPT/Claude/Gemini. Observer + Guide together build it.

```
=== ContextFlow Snapshot — {timestamp} ===
CONTENT TYPE: {content_type}
TITLE: {title}
URL: {url_visible}

WHAT'S ON SCREEN:
{primary_text}

CODE VISIBLE:
{code_blocks joined by \n}

ERRORS DETECTED:
{error_messages joined by \n}

SUGGESTED NEXT QUESTIONS:
{questions_to_ask numbered list}

=== END SNAPSHOT ===
```

User pastes this into any LLM. Zero re-explanation needed.

---

## Data Flow Diagram

```
[macOS Screen]
      │  mss.grab()
      ▼
[capture_node] ──── screenshot_b64 ────▶ [observer_node / Gemini Vision]
                                                    │
                                         extracted_context (JSON)
                                                    │
                                                    ▼
                                        [guide_node / Gemini Text]
                                                    │
                                          guidance + context_package
                                                    │
                                                    ▼
                                           [output_node / CLI or UI]
                                                    │
                                          ┌─── continue? ───┐
                                          │                 │
                                         YES               NO
                                          │                 │
                                    [capture_node]        [END]
```
