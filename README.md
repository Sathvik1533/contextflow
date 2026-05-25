# ContextFlow

> Screen-aware AI learning assistant. One hotkey → AI reads your screen → full context on clipboard.

**Status: Week 3 / 9 — Active development. Building in public.**

---

## The Problem

Every time you ask an AI for help, you spend 2 minutes re-explaining what's on your screen — what tutorial you're watching, what error you're seeing, what code you're reading.

ContextFlow eliminates that permanently.

## How It Works

```
You press the hotkey
    ↓
ContextFlow captures your screen
    ↓
Observer Agent (Groq Vision) reads everything visible — code, errors, docs, video
    ↓
Guide Agent builds personalized advice based on your level and learning goal
    ↓
Full context package copied to clipboard
    ↓
Paste into ChatGPT / Claude / Gemini — zero re-explanation
```

## What Makes It Different

**It knows who you are.** First launch asks 3 questions and reads your terminal history to detect your stack. Saves a profile. Every capture after that adapts to your level — beginner gets plain English, advanced gets architecture.

**It remembers where you stopped.** Come back next day, morning briefing shows your last topic, session count, and what to do next.

**It reads everything.** Code, documentation, error messages, YouTube tutorials — Observer extracts all visible text and structure. Guide turns it into actionable next steps.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Agent orchestration | LangGraph |
| Vision (screen reading) | Groq + Llama 4 Scout |
| Text (guidance) | Groq + Llama 3.3 70B |
| CLI | Rich |
| Screen capture | mss + Pillow |
| User profile | JSON + terminal history analysis |

## Project Structure

```
src/
├── agents/
│   ├── observer.py      # Vision agent — reads screen, returns structured JSON
│   └── guide.py         # Text agent — generates personalized advice
├── capture/
│   ├── screen.py        # mss screen capture
│   └── terminal.py      # shell history reader
├── graph/
│   ├── builder.py       # LangGraph StateGraph wiring
│   ├── nodes.py         # Node functions (capture, observe, guide, output)
│   └── state.py         # ContextFlowState TypedDict
├── onboarding/
│   └── profile.py       # First-launch onboarding, morning briefing, profile persistence
├── output/
│   └── cli.py           # Rich CLI display, clipboard copy
├── utils/
│   └── parser.py        # Content-type-aware context filtering
└── main.py              # Entry point

tests/                   # 39 tests, all passing
```

## Installation

```bash
git clone https://github.com/Sathvik1533/contextflow.git
cd contextflow

# Install with uv (recommended)
pip install uv
uv pip install -e .

# Or with pip
pip install -e .

# Add your Groq API key (free at console.groq.com)
cp .env.example .env
# Edit .env and add: GROQ_API_KEY=your_key_here
```

## Usage

```bash
python src/main.py
```

First launch: answers 3 questions → builds your profile.
Every launch after: morning briefing → capture → clipboard.

Switch to any window during the 3-second countdown. ContextFlow captures whatever is visible.

## Roadmap

| Week | Feature | Status |
|------|---------|--------|
| 1 | LangGraph pipeline, Observer + Guide agents | Done |
| 2 | Content parser, terminal context, session history, rate limit recovery | Done |
| 3 | Onboarding, user profile, morning briefing | Done |
| 4 | ChromaDB memory agent, global hotkey, git context | Next |
| 5 | Video pipeline (YouTube, LinkedIn, Loom → context package) | Planned |
| 6 | Session archive, morning briefing v2, background capture | Planned |
| 7 | Voice commands, FastAPI wrapper | Planned |
| 8 | Tauri desktop overlay (React + Framer Motion) | Planned |
| 9 | Auto-paste to LLM, open source launch | Planned |

## Tests

```bash
python -m pytest tests/ -v
# 39 passed
```

---

Built by [@Sathvik1533](https://github.com/Sathvik1533) — learning AI engineering by shipping real tools.
