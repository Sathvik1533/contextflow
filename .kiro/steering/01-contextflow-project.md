# ContextFlow — Project Steering
# Kiro reads this for every ContextFlow agent operation.
# Architecture decisions are LOCKED unless user explicitly changes them.

---

## PROJECT IDENTITY

**Name:** ContextFlow
**Tagline:** Screen-aware AI learning assistant. No copy-paste. No re-explaining. One hotkey.
**Stack:** Python + LangGraph + Groq API (Llama 4 Scout Vision + Llama 3.3 70B) + mss + rich  
**Constraint:** Free tier only. Groq API. No paid APIs.  
**Platform:** macOS M1 (primary). CLI first, overlay later.  
**Goal:** GitHub portfolio project → internship in AI/ML engineering

**Tech Stack Details:**
- **Agent Framework:** LangGraph + LangChain
- **LLM API:** Groq (free tier) - Llama 4 Scout Vision + Llama 3.3 70B
- **Screen Capture:** mss + Pillow
- **CLI Output:** rich library
- **Hotkey Listener:** pynput (Week 4)
- **Package Manager:** uv (10-100x faster than pip)
- **Python Version:** 3.11 or 3.12 (NOT 3.14 — compatibility issues)

---

## THE PROBLEM BEING SOLVED

When watching YouTube tutorials or reading docs, users cannot share screen context with LLMs.
They must manually copy-paste code, errors, or descriptions — and re-explain everything each time.

ContextFlow solves this: one hotkey → agent reads screen → builds context package → clipboard.
User pastes into any LLM (ChatGPT, Claude, Gemini) — zero re-explanation needed.

---

## AGENT ARCHITECTURE (LOCKED)

### State Schema
```python
class ContextFlowState(TypedDict):
    screenshot_b64: str          # base64 PNG from mss
    capture_timestamp: str       # ISO timestamp
    extracted_context: dict      # Observer JSON output
    guidance: dict               # Guide response
    error: Optional[str]         # Node failures
    loop_count: int              # Capture cycles count
    should_continue: bool        # Graph exit flag
```

### Nodes (execution order)
1. `capture_node` — mss grabs screen → base64 PNG
2. `observer_node` — Gemini Vision → structured JSON (content_type, title, code, errors, confidence)
3. `guide_node` — Gemini Text → summary + learning path + context_package string
4. `output_node` — rich CLI display + clipboard copy
5. `error_node` — catches failures, logs, retries or exits

### Edge Logic
```
capture_node → observer_node
observer_node → guide_node (if confidence > 0.6)
observer_node → capture_node (if confidence ≤ 0.6, re-capture)
guide_node → output_node
output_node → capture_node (if should_continue=True)
output_node → END (if should_continue=False)
any_node → error_node (on exception)
```

### Observer Output Schema (STRICT — no deviation)
```json
{
  "content_type": "youtube|documentation|code|error|other",
  "title": "string",
  "primary_text": "string max 500 chars",
  "code_blocks": ["array of strings"],
  "error_messages": ["array of strings"],
  "url_visible": "string or null",
  "confidence": 0.0
}
```

### Context Package Format (what gets copied to clipboard)
```
=== ContextFlow Snapshot — {timestamp} ===
CONTENT TYPE: {content_type}
TITLE: {title}
URL: {url_visible}

WHAT'S ON SCREEN:
{primary_text}

CODE VISIBLE:
{code_blocks}

ERRORS DETECTED:
{error_messages}

SUGGESTED QUESTIONS FOR LLMs:
{questions_to_ask}
=== END SNAPSHOT ===
```

---

## FOLDER STRUCTURE (enforce this)

```
contextflow/
├── .kiro/
│   ├── steering/
│   ├── specs/
│   └── hooks/
├── src/
│   ├── agents/
│   │   ├── observer.py      # Gemini Vision node
│   │   └── guide.py         # Gemini Text node
│   ├── graph/
│   │   ├── state.py         # ContextFlowState TypedDict
│   │   ├── nodes.py         # All node functions
│   │   └── builder.py       # StateGraph assembly
│   ├── capture/
│   │   └── screen.py        # mss capture + base64 encode
│   ├── output/
│   │   └── cli.py           # rich display + pbcopy
│   └── main.py              # Entry point + hotkey listener
├── tests/
│   ├── test_capture.py
│   ├── test_observer.py
│   └── test_guide.py
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

---

## DEPENDENCY LIST (free tier only)

```toml
[project]
dependencies = [
    "langgraph>=0.2.0",
    "langchain-google-genai>=2.0.0",
    "langchain-core>=0.3.0",
    "mss>=9.0.0",
    "Pillow>=10.0.0",
    "python-dotenv>=1.0.0",
    "rich>=13.0.0",
    "pynput>=1.7.0",
]
```

Install: `uv pip install -e .` (not pip)

---

## MILESTONES (Kiro follows this sequence, never skips)

### Milestone 1 — Observer Alive (Week 1)
- [ ] GitHub repo created via MCP
- [ ] pyproject.toml + .gitignore + .env.example
- [ ] capture_node: mss → base64 PNG
- [ ] observer_node: base64 → Gemini Vision → valid JSON
- [ ] JSON validates against Observer schema
- [ ] `python src/main.py` → prints JSON to terminal
- **Gate:** Valid JSON from 3 different screen types (YouTube, docs, code)

### Milestone 2 — Full Graph Loop (Week 2)
- [ ] ContextFlowState TypedDict
- [ ] guide_node: extracted_context → guidance dict
- [ ] output_node: rich display
- [ ] error_node: catches + logs
- [ ] StateGraph assembled with conditional edges
- [ ] Manual trigger: Enter key → full loop runs
- [ ] Context package string generated
- **Gate:** Full loop runs 5x without error on different content

### Milestone 3 — Hardening (Week 3)
- [ ] Content-type-specific Guide prompts
- [ ] Rate limit handling (exponential backoff on 429)
- [ ] Save snapshot to ~/.contextflow/sessions/
- [ ] Test on YouTube, docs, VS Code, blank screen
- **Gate:** 3 content types → meaningfully different guidance

### Milestone 4 — Hotkey + Clipboard (Week 4)
- [ ] pynput global hotkey: Cmd+Shift+Space
- [ ] Context package → pbcopy (macOS clipboard)
- [ ] rich spinner during API calls
- [ ] Config: ~/.contextflow/config.toml
- [ ] README with demo GIF
- [ ] Repo public, CI added
- **Gate:** Hotkey → clipboard → paste into Claude → it understands without re-explanation

---

## WHAT NOT TO BUILD (Kiro must not touch these in Weeks 1-4)

- No Swift, no Xcode, no AppKit
- No vector database or embeddings
- No LangSmith tracing (Week 5+)
- No auto-polling (rate limits + battery)
- No settings UI
- No "export to Notion" or external integrations
- No lil-agents copy — UI is original when built

---

## LINKEDIN/INSTA POST SCHEDULE (Kiro reminds at each gate)

| Gate | Post trigger |
|------|-------------|
| M1 complete | "Built screen-aware AI in Python. Observer returns structured JSON from my screen." |
| M2 complete | "Multi-agent loop working. LangGraph + Gemini Flash. Zero API cost." |
| M3 complete | "Context-aware: different guidance for YouTube vs docs vs code errors." |
| M4 complete | "Shipped v0.1. One hotkey. AI reads screen. Context on clipboard." |

Post working demos only. No idea posts without code.
