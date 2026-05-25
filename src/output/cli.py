"""CLI output utilities using rich library.

This module handles displaying guidance to the user in a beautiful terminal UI
and copying the context package to the clipboard.
"""

import subprocess
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def display_guidance(guidance: dict[str, Any], loop_count: int) -> None:
    """Display guidance in beautiful CLI format using rich.
    
    Args:
        guidance: Dict with keys:
            - summary: str
            - learning_path: List[str]
            - questions_to_ask: List[str]
            - context_package: str
        loop_count: Number of capture cycles completed
    """
    console.print()
    console.print("=" * 70, style="bold cyan")
    console.print(f"  ContextFlow — Capture #{loop_count}", style="bold cyan")
    console.print("=" * 70, style="bold cyan")
    console.print()
    
    # Summary
    summary_text = Text(guidance.get("summary", "No summary available"))
    summary_panel = Panel(
        summary_text,
        title="📝 Summary",
        border_style="green",
        padding=(1, 2),
    )
    console.print(summary_panel)
    console.print()
    
    # Learning Path
    learning_path = guidance.get("learning_path", [])
    if learning_path:
        path_text = Text()
        for i, step in enumerate(learning_path, 1):
            path_text.append(f"{i}. ", style="bold yellow")
            path_text.append(f"{step}\n", style="white")
        
        path_panel = Panel(
            path_text,
            title="🎯 Learning Path",
            border_style="blue",
            padding=(1, 2),
        )
        console.print(path_panel)
        console.print()
    
    # Questions
    questions = guidance.get("questions_to_ask", [])
    if questions:
        questions_text = Text()
        for i, question in enumerate(questions, 1):
            questions_text.append(f"{i}. ", style="bold magenta")
            questions_text.append(f"{question}\n", style="white")
        
        questions_panel = Panel(
            questions_text,
            title="❓ Questions to Ask LLMs",
            border_style="magenta",
            padding=(1, 2),
        )
        console.print(questions_panel)
        console.print()


def copy_to_clipboard(text: str) -> bool:
    """Copy text to clipboard. Works on macOS, Linux, Windows.

    macOS → pbcopy
    Linux → xclip (if installed)
    Windows → clip
    """
    import sys
    try:
        if sys.platform == "darwin":
            cmd = ["pbcopy"]
        elif sys.platform == "win32":
            cmd = ["clip"]
        else:
            cmd = ["xclip", "-selection", "clipboard"]

        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        process.communicate(input=text.encode("utf-8"))
        return process.returncode == 0
    except Exception:
        return False


def prompt_continue() -> bool:
    """Ask user if they want to continue or quit.
    
    Returns:
        True if user wants to continue, False to quit
    """
    console.print()
    console.print("[bold cyan]Options:[/bold cyan]")
    console.print("  [C]ontinue — Capture again")
    console.print("  [Q]uit — Exit ContextFlow")
    console.print()
    
    while True:
        choice = console.input("[bold yellow]Your choice (C/Q):[/bold yellow] ").strip().lower()
        
        if choice in ["c", "continue"]:
            return True
        elif choice in ["q", "quit"]:
            return False
        else:
            console.print("[red]Invalid choice. Please enter C or Q.[/red]")
