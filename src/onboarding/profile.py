"""Onboarding and User Profile Management.

TASK-012: First-launch detection, 3-question onboarding,
terminal signal analysis, profile persistence, morning briefing.

WHY THIS EXISTS:
Every AI tool treats all users identically. ContextFlow doesn't.
We build a profile on first launch, then every capture personalizes
to that profile. Guide depth, question difficulty, learning path
complexity — all adapt to who you are.

Profile stored at: ~/.contextflow/profile.json
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel

console = Console()

PROFILE_DIR = Path.home() / ".contextflow"
PROFILE_PATH = PROFILE_DIR / "profile.json"


# ─── Public API ───────────────────────────────────────────────────────────────

def load_or_create_profile() -> dict[str, Any]:
    """Entry point called by main.py on every startup.

    First launch  → run onboarding questions + terminal analysis → save profile
    Return visit  → load profile → show morning briefing → return profile

    Returns the profile dict always. Downstream (guide_node) reads user_level from it.
    """
    if PROFILE_PATH.exists():
        profile = _load_profile()
        _show_morning_briefing(profile)
        return profile
    else:
        return _run_onboarding()


def update_profile_after_session(profile: dict, session_history: list[dict]) -> None:
    """Called by output_node after each completed session.

    Updates: last_seen, session_count, topics_seen.
    Saves back to disk so morning briefing has fresh data.
    """
    profile["last_seen"] = datetime.now().isoformat()
    profile["session_count"] = profile.get("session_count", 0) + 1

    for entry in session_history:
        ct = entry.get("content_type", "unknown")
        title = entry.get("title", "")
        if ct and ct != "unknown":
            topics = profile.setdefault("topics_seen", {})
            topics[ct] = topics.get(ct, 0) + 1
        if title:
            recent = profile.setdefault("recent_titles", [])
            recent.append(title)
            profile["recent_titles"] = recent[-10:]  # Keep last 10

    _save_profile(profile)


# ─── First Launch: Onboarding ─────────────────────────────────────────────────

def _run_onboarding() -> dict[str, Any]:
    """Run the 3-question onboarding flow on first launch.

    WHY 3 QUESTIONS:
    More than 3 = friction, user quits. Fewer = not enough signal.
    Terminal history fills the gaps silently in the background.

    WHAT EACH QUESTION GIVES US:
    Q1 (role)       → context for Guide's framing ("as a student..." vs "as an engineer...")
    Q2 (stack)      → which code types to prioritize in Observer classification
    Q3 (level)      → Guide prompt depth (beginner = plain English, advanced = architecture)
    """
    console.print()
    console.print(Panel(
        "[bold cyan]Welcome to ContextFlow[/bold cyan]\n\n"
        "First launch — 3 quick questions to personalize everything.\n"
        "[dim]Takes 30 seconds. You can update this anytime.[/dim]",
        border_style="cyan",
        padding=(1, 2),
    ))
    console.print()

    # Q1: Role
    console.print("[bold yellow]1. What best describes you?[/bold yellow]")
    console.print("   [1] Student / learner")
    console.print("   [2] Junior developer (0-2 years)")
    console.print("   [3] Mid-level developer (2-5 years)")
    console.print("   [4] Senior developer (5+ years)")
    console.print("   [5] Designer / PM / non-engineer")
    console.print()

    role_map = {
        "1": "student", "2": "junior", "3": "mid",
        "4": "senior", "5": "non-engineer",
    }
    role_raw = _prompt_choice("Your choice (1-5): ", valid=set(role_map.keys()))
    role = role_map[role_raw]

    # Q2: Primary tech stack
    console.print()
    console.print("[bold yellow]2. What's your primary tech stack?[/bold yellow]")
    console.print("   [dim](e.g. Python, React, Node.js, Flutter — type freely)[/dim]")
    console.print()
    stack = console.input("   → ").strip() or "not specified"

    # Q3: Learning goal right now
    console.print()
    console.print("[bold yellow]3. What's your main learning goal this month?[/bold yellow]")
    console.print("   [dim](e.g. 'learning LangGraph', 'landing first job', 'building side projects')[/dim]")
    console.print()
    goal = console.input("   → ").strip() or "general learning"

    # Derive user_level from role
    level_map = {
        "student": "beginner",
        "junior": "beginner",
        "mid": "intermediate",
        "senior": "advanced",
        "non-engineer": "beginner",
    }
    user_level = level_map[role]

    # Analyze terminal history for bonus signal
    console.print()
    console.print("[dim]Analyzing your terminal history for additional context...[/dim]")
    terminal_signal = _analyze_terminal_for_profile()

    # Merge terminal signal into stack if we found something
    if terminal_signal.get("detected_stack") and stack == "not specified":
        stack = terminal_signal["detected_stack"]
        console.print(f"[green]Detected stack from terminal: {stack}[/green]")

    # Build profile
    profile: dict[str, Any] = {
        "role": role,
        "user_level": user_level,
        "stack": stack,
        "goal": goal,
        "created_at": datetime.now().isoformat(),
        "last_seen": datetime.now().isoformat(),
        "session_count": 0,
        "topics_seen": {},
        "recent_titles": [],
        "terminal_signal": terminal_signal,
    }

    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    _save_profile(profile)

    console.print()
    console.print(Panel(
        f"[bold green]Profile created.[/bold green]\n\n"
        f"Level: [cyan]{user_level}[/cyan]\n"
        f"Stack: [cyan]{stack}[/cyan]\n"
        f"Goal:  [cyan]{goal}[/cyan]\n\n"
        f"[dim]Saved to ~/.contextflow/profile.json[/dim]",
        border_style="green",
        padding=(1, 2),
    ))
    console.print()

    return profile


# ─── Return Visit: Morning Briefing ──────────────────────────────────────────

def _show_morning_briefing(profile: dict) -> None:
    """Show a briefing for returning users.

    WHY THIS MATTERS:
    Without this, every session starts from zero. You open ContextFlow,
    you've forgotten where you stopped yesterday. The briefing gives you
    a 5-second re-entry into your last learning state.

    Only shows if last session was >1 hour ago (not spammy for same-session restarts).
    """
    last_seen_str = profile.get("last_seen", "")
    if last_seen_str:
        try:
            last_seen = datetime.fromisoformat(last_seen_str)
            hours_since = (datetime.now() - last_seen).total_seconds() / 3600
            if hours_since < 1:
                return  # Same session restart — skip briefing
        except ValueError:
            pass

    session_count = profile.get("session_count", 0)
    goal = profile.get("goal", "general learning")
    recent_titles = profile.get("recent_titles", [])
    topics_seen = profile.get("topics_seen", {})
    user_level = profile.get("user_level", "intermediate")

    # Build briefing content
    lines = [
        f"[bold cyan]Welcome back.[/bold cyan] Session #{session_count + 1}\n",
        f"Goal:  [cyan]{goal}[/cyan]",
        f"Level: [cyan]{user_level}[/cyan]",
    ]

    if recent_titles:
        lines.append(f"\nLast topic: [yellow]{recent_titles[-1][:60]}[/yellow]")

    if topics_seen:
        top_type = max(topics_seen, key=lambda k: topics_seen[k])
        lines.append(f"Most captured: [yellow]{top_type}[/yellow] ({topics_seen[top_type]} captures)")

    if recent_titles and len(recent_titles) >= 2:
        lines.append(f"\n[dim]Recent: {' → '.join(t[:30] for t in recent_titles[-3:])}[/dim]")

    console.print()
    console.print(Panel(
        "\n".join(lines),
        title="Morning Briefing",
        border_style="cyan",
        padding=(1, 2),
    ))
    console.print()


# ─── Terminal Signal Analysis ─────────────────────────────────────────────────

def _analyze_terminal_for_profile() -> dict[str, Any]:
    """Read terminal history to infer tech stack without asking.

    WHY TERMINAL AS SIGNAL:
    What you install, run, and debug is a more honest signal than
    what you say you use. npm install = JS dev. pip install torch = ML.
    docker-compose = backend. kubectl = DevOps.

    FALLBACK GUARANTEE:
    If no history file → returns empty dict. Never crashes.
    Never blocks onboarding. Terminal signal is bonus, not required.
    """
    try:
        from src.capture.terminal import capture_terminal_context
        ctx = capture_terminal_context()
        commands = ctx.get("recent_commands", [])

        if not commands:
            return {"detected_stack": None, "signals": []}

        signals = []
        stack_votes: dict[str, int] = {}

        # Stack detection patterns
        patterns = {
            "Python": ["python", "pip", "uv", "pytest", "uvicorn", "fastapi", "django", "flask"],
            "JavaScript/React": ["npm", "npx", "yarn", "bun", "vite", "react", "next", "node"],
            "Rust": ["cargo", "rustc", "rust"],
            "Go": ["go build", "go run", "go test", "go mod"],
            "Flutter/Dart": ["flutter", "dart"],
            "Docker/DevOps": ["docker", "kubectl", "helm", "terraform"],
            "ML/AI": ["torch", "tensorflow", "huggingface", "ollama", "langchain", "langgraph"],
            "Java/Kotlin": ["mvn", "gradle", "kotlinc", "javac"],
        }

        all_commands_str = " ".join(commands).lower()

        for stack_name, keywords in patterns.items():
            for kw in keywords:
                if kw in all_commands_str:
                    stack_votes[stack_name] = stack_votes.get(stack_name, 0) + 1
                    signals.append(f"{kw} → {stack_name}")
                    break

        # Pick top stack by vote count
        detected = max(stack_votes, key=lambda k: stack_votes[k]) if stack_votes else None

        return {
            "detected_stack": detected,
            "signals": signals[:5],  # Top 5 signals
            "shell_type": ctx.get("shell_type", "unknown"),
        }

    except Exception:
        return {"detected_stack": None, "signals": []}


# ─── Persistence ──────────────────────────────────────────────────────────────

def _load_profile() -> dict[str, Any]:
    with open(PROFILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_profile(profile: dict) -> None:
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)


def _prompt_choice(prompt_text: str, valid: set[str]) -> str:
    while True:
        choice = console.input(f"   [bold yellow]{prompt_text}[/bold yellow]").strip()
        if choice in valid:
            return choice
        console.print(f"[red]Please enter one of: {', '.join(sorted(valid))}[/red]")
