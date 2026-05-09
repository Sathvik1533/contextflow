# ContextFlow — Requirements Spec
# Kiro uses this to understand WHAT to build before HOW.

---

## Problem Statement

Developers watching YouTube tutorials or reading documentation must manually:
1. Pause video
2. Copy-paste code/errors
3. Switch to LLM tab
4. Re-explain the entire context
5. Wait for response
6. Switch back

This "context switching friction" kills learning flow. Average: 3-5 minutes lost per context switch.

---

## Solution

ContextFlow eliminates all 5 steps.

User presses one hotkey → system captures screen → AI reads it → builds complete context package → copies to clipboard. User pastes into any LLM. Zero re-explanation.

---

## Functional Requirements

### FR-01: Screen Capture
- System MUST capture primary monitor on hotkey trigger
- Capture MUST complete in <2 seconds
- Image MUST be resized to 1280x800 before API call (token cost reduction)
- Image MUST be base64 encoded for Vision API

### FR-02: Observer Agent
- System MUST send captured image to Groq Vision API (llama-3.2-11b-vision-preview)
- Observer MUST return structured JSON matching defined schema
- Observer MUST classify content_type: youtube, documentation, code, error, other
- Observer MUST include confidence score (0.0-1.0)
- If confidence < 0.6: re-capture (not fail)
- Observer MUST strip markdown fences from API response before JSON parse

### FR-03: Guide Agent
- Guide MUST use Groq Text API (llama-3.3-70b-versatile)
- Guide MUST return: summary (2-3 sentences), learning_path (3 steps), questions_to_ask (2 prompts)
- Guide MUST build context_package string formatted for pasting into external LLMs
- Guide prompts MUST be content-type-specific (YouTube != docs != code != error)

### FR-04: Context Package
- Plain text only (no markdown)
- Self-contained: LLM reading it needs zero additional explanation
- Includes: content_type, title, URL, primary_text, code_blocks, error_messages, suggested questions

### FR-05: Output
- Display guidance in terminal via rich
- Copy context_package to macOS clipboard (pbcopy)
- Confirm: "Context copied to clipboard. Paste into any LLM."
- Show loop_count and timestamp

### FR-06: Hotkey Trigger
- Global hotkey: Cmd+Shift+Space
- Works when any other app is in focus
- Shows rich spinner during API processing

### FR-07: Error Handling
- Catch API failures without crashing
- Handle 429 with exponential backoff: 5s, 10s, 20s
- Log errors to ~/.contextflow/logs/
- Display human-readable error (not stack trace)

### FR-08: Session Storage
- Save each snapshot to ~/.contextflow/sessions/YYYY-MM-DD/
- Each snapshot = JSON file with full state
- [S] key manually saves snapshot during output display

---

## Non-Functional Requirements

- Cost: free tier only (<15 API calls/min)
- Performance: full cycle <8 seconds on M1
- Privacy: screenshots never stored permanently
- Reliability: handles Vision API returning prose, mss permission denied, missing .env

---

## Out of Scope (v0.1)

- macOS overlay UI (Week 5+)
- Multi-monitor, auto-polling, web dashboard, cloud sync, Windows/Linux
