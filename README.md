# ContextFlow

> **Status:** 🚧 Week 1 — Under Active Development

Screen-aware AI learning assistant. No copy-paste. No re-explaining. One hotkey.

## The Problem

When watching YouTube tutorials or reading docs, you can't share screen context with LLMs. You must manually copy-paste code, errors, or descriptions — and re-explain everything each time.

## The Solution

**One hotkey** → AI reads your screen → builds context package → clipboard.  
Paste into any LLM (ChatGPT, Claude, Gemini) — zero re-explanation needed.

## Tech Stack

- **Agent Framework:** LangGraph + LangChain
- **LLM:** Google Gemini 2.0 Flash (Vision + Text)
- **Screen Capture:** mss + Pillow
- **CLI:** rich + pynput
- **Platform:** macOS M1 (primary)
- **Constraint:** Free tier only

## Architecture

Multi-agent loop:
```
Screen Capture → Observer (Vision) → Guide (Text) → Context Package → Clipboard
       ↑                                                                    |
       └────────────────────── User continues ──────────────────────────────┘
```

## Roadmap

- [x] Week 1: Observer agent alive (Gemini Vision → structured JSON)
- [ ] Week 2: Full LangGraph loop (Observer → Guide → Output)
- [ ] Week 3: Content-type-specific guidance (YouTube ≠ docs ≠ code)
- [ ] Week 4: Hotkey trigger + clipboard integration

## Why This Exists

Portfolio project for AI/ML engineering internship applications. Building in public. Learning by shipping.

---

**Check back in 4 weeks for the full demo.**
