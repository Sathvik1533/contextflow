# design.md — ContextFlow UI & Handoff Design

## The Core Question: CLI First or Mac Overlay First?

Mac overlay first = wrong move. Reason: SwiftUI/AppKit integration with Python is a bridge (via subprocess or socket). Building that bridge before the Python logic is proven = debugging two systems at once. You'll never know if the bug is in the AI or the bridge.

**Decision: CLI for Milestone 1. Mac overlay at Week 5+.**

The CLI IS the product for now. It's not a compromise — it's discipline.

---

## Milestone 1 UI: The Terminal

```
┌──────────────────────────────────────────────────────┐
│  ContextFlow v0.1 — Observer-Guide Loop              │
│  ──────────────────────────────────────────────────  │
│  [12:34:01] Capturing screen...                      │
│  [12:34:02] Observer: Detected YouTube tutorial      │
│             Title: "LangGraph Crash Course"          │
│             Confidence: 0.91                         │
│                                                      │
│  [12:34:04] Guide Response:                          │
│  ─────────────────────────────────────               │
│  SUMMARY: You're watching a LangGraph tutorial.      │
│  The speaker is explaining StateGraph initialization.│
│                                                      │
│  NEXT STEPS:                                         │
│  1. Pause at 4:32 — that's where State schema shows  │
│  2. Open docs.langchain.com/langgraph                │
│  3. Try: "What is TypedDict in Python LangGraph?"    │
│                                                      │
│  CONTEXT PACKAGE (copy → paste into any LLM):       │
│  ┌────────────────────────────────────────────────┐  │
│  │ === ContextFlow Snapshot — 2025-01-15 12:34 ===│  │
│  │ CONTENT TYPE: youtube                          │  │
│  │ TITLE: LangGraph Crash Course                  │  │
│  │ ...                                            │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  [C]ontinue  [Q]uit  [S]ave snapshot                 │
└──────────────────────────────────────────────────────┘
```

---

## Observer → Guide Handoff Contract

This is the most critical design decision. Observer must output **strict JSON**. If it outputs prose, Guide breaks.

**Observer prompt (enforces schema):**
```
You are a screen analysis agent. Analyze this screenshot and respond ONLY with valid JSON.
No prose, no markdown, no explanation. JSON only.

Schema:
{
  "content_type": "youtube|documentation|code|error|other",
  "title": "string — page or video title",
  "primary_text": "string — main readable content, max 500 chars",
  "code_blocks": ["array of code strings visible"],
  "error_messages": ["array of error/stack trace strings"],
  "url_visible": "string or null",
  "confidence": 0.0-1.0
}
```

**Guide prompt (uses Observer JSON):**
```
You are a learning guide. A screen analysis agent has captured what a developer is looking at.

Screen context:
{extracted_context as formatted string}

Respond with:
1. SUMMARY (2-3 sentences, plain language)
2. NEXT STEPS (3 actionable items)
3. QUESTIONS TO ASK (2 suggested prompts for external LLMs)
4. CONTEXT PACKAGE (full snapshot formatted for pasting into ChatGPT/Claude/Gemini)
```

---

## UI Evolution Path

| Phase | UI | Why |
|-------|-----|-----|
| M1 (Week 1-2) | Python CLI, rich library | Zero setup friction. Focus on agent logic |
| M2 (Week 3-4) | CLI + keyboard shortcut trigger (pynput) | User controls when to capture, not polling |
| M3 (Week 5-6) | Tauri app (Rust shell + HTML frontend) | Cross-platform, 10x lighter than Electron |
| M4 (Week 7-8) | macOS overlay via NSPanel | Vibes-first, transparent, always-on-top |

**Why Tauri over Electron:** Electron bundles Chromium (~150MB). Tauri uses system WebView (~8MB). On M1, Tauri feels native. Electron feels like a webpage.

**Why not Swift first:** Python-Swift bridge requires XPC or sockets. Adds 1-2 weeks of infra before any AI logic is testable. Build the brain first, wrap it second.

---

## The "Viby" UI — Future State Reference

When you get to M4, the vision:

- Transparent NSPanel, 320px wide, right side of screen
- Always-on-top, no dock icon
- Triggered by: `Cmd+Shift+Space` (global hotkey)
- Shows last Guide response as compact card
- "Copy context" button → copies context package to clipboard
- Character (lil-agents inspired) = loading indicator only, not core feature

This is Week 7+. Don't design it now. Design decisions made before you have real usage data are usually wrong.

---

## Key Risk: Free Tier Rate Limits

Gemini 2.0 Flash free tier: ~15 requests/minute, 1500/day.
Every capture cycle = 2 requests (Observer + Guide).
At 1 capture per 30 seconds: 4 req/min = safe.
At 1 capture per 5 seconds: 24 req/min = will hit limits.

**Mitigation:** Don't auto-poll. Capture on user trigger (hotkey). This also makes the tool less annoying.
