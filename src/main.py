"""ContextFlow - Main Entry Point

Run this to start the ContextFlow system.

Usage:
    python src/main.py
"""

import os
import sys

from dotenv import load_dotenv
from rich.console import Console

from src.utils.logger import get_logger, setup_logging

load_dotenv()
setup_logging()   # must be first — sets up log file before anything else runs

console = Console()
logger = get_logger(__name__)


def startup_check() -> bool:
    """Feature 3 — Pre-flight check before graph starts.

    Verifies: .env exists, GROQ_API_KEY set, mss can take a screenshot.
    Shows one clear error message if anything is missing.
    Returns True if all checks pass, False if startup should abort.
    """
    console.print("\n[bold cyan]Running startup checks...[/bold cyan]")
    all_ok = True

    # Check 1: GROQ_API_KEY
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        console.print("[red]GROQ_API_KEY not found.[/red]")
        console.print("   Create a .env file with: GROQ_API_KEY=your_key_here")
        console.print("   Get a free key at: console.groq.com/keys")
        all_ok = False
    else:
        console.print("[green]  API key found[/green]")

    # Check 2: Screen capture permission (mss test)
    try:
        import mss
        with mss.MSS() as sct:
            if len(sct.monitors) < 2:
                console.print("[red]  No monitors detected.[/red]")
                all_ok = False
            else:
                console.print("[green]  Screen capture ready[/green]")
    except Exception as e:
        console.print(f"[red]  Screen capture failed: {e}[/red]")
        console.print("   On macOS: System Settings → Privacy → Screen Recording → allow Terminal/VS Code")
        all_ok = False

    # Check 3: Internet connectivity (quick DNS check)
    try:
        import socket
        socket.setdefaulttimeout(3)
        socket.getaddrinfo("api.groq.com", 443)
        console.print("[green]  Internet connection OK[/green]")
    except Exception:
        console.print("[red]  No internet connection detected.[/red]")
        console.print("   ContextFlow needs Groq API access. Check your network.")
        all_ok = False

    if all_ok:
        console.print("[bold green]All checks passed.[/bold green]\n")
    else:
        console.print("\n[bold red]Fix the issues above and run again.[/bold red]\n")

    return all_ok


def main():
    """Main entry point for ContextFlow."""

    console.print("\n" + "=" * 70, style="bold cyan")
    console.print("  ContextFlow — Screen-Aware AI Dev Companion", style="bold cyan")
    console.print("=" * 70 + "\n", style="bold cyan")

    console.print("What this does:", style="bold yellow")
    console.print("   1. Captures your screen (3s delay — switch tabs)")
    console.print("   2. AI reads what's visible")
    console.print("   3. Generates actionable advice")
    console.print("   4. Copies context package to clipboard")
    console.print("   5. Paste into ChatGPT/Claude/Gemini — zero re-explanation\n")

    # Feature 3: startup check
    if not startup_check():
        sys.exit(1)

    # TASK-012: Load or create user profile (onboarding on first launch, briefing on return)
    from src.onboarding.profile import load_or_create_profile
    profile = load_or_create_profile()
    user_level = profile.get("user_level", "intermediate")

    # Ask for session intent — what they're learning RIGHT NOW (different from long-term goal)
    console.print("What are you trying to learn right now?", style="bold yellow")
    console.print(f"   [dim](Press Enter to use your goal: \"{profile.get('goal', 'general learning')}\")[/dim]\n")
    user_intent = console.input("   [bold yellow]→[/bold yellow] ").strip()
    if not user_intent:
        user_intent = profile.get("goal", "general learning")

    console.print(f"\n[green]Got it: {user_intent}[/green]\n")

    # Build graph
    from src.graph.builder import build_graph
    app = build_graph()

    initial_state = {
        "screenshot_b64": "",
        "capture_timestamp": "",
        "user_intent": user_intent,
        "user_level": user_level,
        "session_history": [],
        "extracted_context": {},
        "terminal_context": {},
        "memory_context": {},
        "guidance": {},
        "error": None,
        "loop_count": 0,
        "retry_count": 0,
        "should_continue": True,
        "profile": profile,
    }

    console.print("=" * 70 + "\n", style="cyan")

    try:
        result = app.invoke(initial_state)

        if result.get("error"):
            console.print(f"\n[red]Error: {result.get('error')}[/red]")

        # TASK-012: Update profile with session data so morning briefing has fresh info
        from src.onboarding.profile import update_profile_after_session
        update_profile_after_session(profile, result.get("session_history", []))

        console.print("\n" + "=" * 70, style="cyan")
        console.print("[bold green]Session complete.[/bold green]")
        console.print(f"   Total captures: {result.get('loop_count', 0)}", style="green")
        console.print("=" * 70 + "\n", style="cyan")

    except KeyboardInterrupt:
        console.print("\n\n[yellow]Interrupted. Exiting...[/yellow]")
    except Exception as e:
        console.print(f"\n\n[bold red]Error: {str(e)}[/bold red]")
        console.print("   Check your .env file and API keys.", style="red")


if __name__ == "__main__":
    main()
