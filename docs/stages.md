# stages.md — ContextFlow 4-Week Roadmap

## North Star
End of Week 4: Hotkey → captures screen → Observer extracts context → Guide gives learning path → context package on clipboard. No UI yet. Agent loop proven.

---

## Week 1 — Environment + Observer Alive

**Goal:** Gemini Vision describes a screenshot. Nothing more.

| Task | Done? |
|------|-------|
| Python 3.11+ venv created | ☐ |
| `mss`, `langgraph`, `langchain-google-genai`, `pillow`, `rich` installed | ☐ |
| Google AI Studio API key in `.env` | ☐ |
| `capture_node` function: mss → base64 PNG | ☐ |
| `observer_node` function: base64 → Gemini Vision → raw JSON | ☐ |
| JSON response validates against State schema | ☐ |
| Manual test: run script, see JSON in terminal | ☐ |

**LinkedIn/Insta post trigger:** Observer returns valid JSON for first time. Post: screenshot of terminal showing structured JSON extracted from your screen. Caption: "Taught an AI to read my screen. Step 1 of building ContextFlow — a screen-aware learning assistant. No copy-paste. Agent does it."

**Milestone gate:** `python observer_test.py` → prints valid `extracted_context` JSON. Green = move to Week 2.

---

## Week 2 — Guide Alive + LangGraph Loop

**Goal:** Full Observer→Guide cycle running as LangGraph graph.

| Task | Done? |
|------|-------|
| `ContextFlowState` TypedDict defined | ☐ |
| `guide_node` function: extracted_context → guidance dict | ☐ |
| `output_node`: pretty-prints guidance with `rich` | ☐ |
| `error_node`: catches API failures, logs, sets should_continue=False | ☐ |
| LangGraph `StateGraph` assembled with all 4 nodes | ☐ |
| Conditional edge logic: loop or END | ☐ |
| Manual trigger: press Enter → captures → prints guidance | ☐ |
| Context package string generated and printed | ☐ |

**LinkedIn/Insta post trigger:** Full loop works end-to-end. Post: screen recording (QuickTime, free) of terminal — you press Enter, 3 seconds later guidance appears. Caption: "Multi-agent loop working. Observer sees screen. Guide tells me what to do next. Built with LangGraph + Gemini Flash. Zero API cost."

**Milestone gate:** Full graph run completes without error 5 times in a row on different screen content.

---

## Week 3 — Hardening + Content Types

**Goal:** System handles YouTube, docs, and code editors correctly. Doesn't break on edge cases.

| Task | Done? |
|------|-------|
| Test on YouTube tutorial screen | ☐ |
| Test on docs page (LangChain docs, MDN, etc.) | ☐ |
| Test on VS Code with error visible | ☐ |
| Test on blank/irrelevant screen (confidence < 0.6 path) | ☐ |
| Content-type-specific Guide prompts (YouTube ≠ docs ≠ code) | ☐ |
| Rate limit handling: exponential backoff on 429 errors | ☐ |
| `[S]ave snapshot` → writes context package to `.txt` file | ☐ |
| Session log: all snapshots saved to `~/.contextflow/sessions/` | ☐ |

**LinkedIn/Insta post trigger:** Demo with 3 content types. Post side-by-side: YouTube snapshot vs docs snapshot vs code error snapshot — different guidance for each. Caption: "ContextFlow now understands context, not just pixels."

**Milestone gate:** 3 content types produce meaningfully different guidance responses.

---

## Week 4 — Hotkey Trigger + Polish

**Goal:** No more pressing Enter. Global hotkey fires the loop.

| Task | Done? |
|------|-------|
| `pynput` global hotkey listener (Cmd+Shift+Space) | ☐ |
| Background thread: hotkey → triggers graph run | ☐ |
| Context package auto-copied to macOS clipboard (`pbcopy`) | ☐ |
| `rich` progress spinner during API calls | ☐ |
| Config file: `~/.contextflow/config.toml` (API key, hotkey, monitor index) | ☐ |
| README written, repo made public | ☐ |
| Demo video recorded (≤60 seconds) | ☐ |

**LinkedIn/Insta post trigger:** Week 4 completion = first public release post. Post the 60-second demo video. Caption: "Shipped v0.1 of ContextFlow. Press one hotkey. AI reads your screen. Gives you a learning path. Context package ready to paste into any LLM. Built with LangGraph + Gemini Flash. Free to run. Repo in comments."

**Milestone gate:** Hotkey fires → context package on clipboard → paste into Claude/ChatGPT → it understands what you were looking at without any explanation.

---

## Post Week 4: What Comes Next

| Week | Target |
|------|--------|
| 5-6 | Tauri shell around the CLI output (first "UI") |
| 7-8 | macOS NSPanel overlay, always-on-top |
| 9+ | Multi-monitor support, LangSmith tracing, session history viewer |

---

## What NOT to Build (Week 1-4)

- No Swift. No Xcode. No AppKit.
- No vector database / embeddings.
- No LangSmith tracing (add in Week 5+).
- No auto-polling (rate limits, battery drain, annoyance).
- No settings UI. Config file is enough.
- No "export to Notion" or integrations. Context package = plain text. That's the integration.
