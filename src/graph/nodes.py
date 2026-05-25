"""LangGraph node functions for ContextFlow.

Each node is a function that:
1. Receives the current state (ContextFlowState)
2. Does work (capture screen, call API, display output)
3. Returns a dict with updated fields to merge into state

LangGraph automatically merges the returned dict into the state.
"""

import time

from rich.console import Console

from src.agents.guide import run_guide
from src.agents.observer import run_observer
from src.capture.screen import capture_screen
from src.capture.terminal import capture_terminal_context
from src.graph.state import ContextFlowState
from src.output.cli import copy_to_clipboard, display_guidance, prompt_continue

console = Console()


MAX_CAPTURE_RETRIES = 3  # Bug fix: prevent infinite low-confidence loop


def capture_node(state: ContextFlowState) -> dict:
    """Entry point: Capture screen AND terminal context.

    Includes a 3-second delay so user can switch to the window they want captured.
    Tracks retry_count to prevent infinite loop when confidence stays below 0.6.
    """
    try:
        # Feature 1: Visible countdown so user knows exactly when to switch tabs
        for i in range(3, 0, -1):
            console.print(f"[bold yellow]Capturing in {i}...[/bold yellow]", end="\r")
            time.sleep(1)
        console.print("[bold green]Capturing now!         [/bold green]")

        screen_result = capture_screen(monitor_index=1, resize_to=(1280, 800))
        terminal_result = capture_terminal_context()

        # Increment retry_count — tracks low-confidence re-capture attempts
        retry_count = state.get("retry_count", 0) + 1

        return {
            "screenshot_b64": screen_result["screenshot_b64"],
            "capture_timestamp": screen_result["capture_timestamp"],
            "terminal_context": terminal_result,
            "retry_count": retry_count,
            "error": None,
        }
    except Exception as e:
        return {
            "error": f"Capture failed: {str(e)}",
            "should_continue": False,
        }



def observer_node(state: ContextFlowState) -> dict:
    """Observer Agent: Analyze screenshot and extract structured context.
    
    This node:
    - Reads screenshot_b64 from state
    - Reads user_intent from state (for priority decisions)
    - Sends to Groq Vision API (meta-llama/llama-4-scout-17b-16e-instruct)
    - Parses response into structured JSON
    - Writes extracted_context to state
    
    If confidence < 0.6, the graph will trigger a re-capture via conditional edge.
    
    Args:
        state: Current graph state with screenshot_b64 and user_intent fields
    
    Returns:
        dict with extracted_context key (or error if API fails)
    """
    try:
        # Get the screenshot from state
        screenshot_b64 = state.get("screenshot_b64")
        if not screenshot_b64:
            return {
                "error": "observer_node: No screenshot_b64 in state",
                "should_continue": False,
            }
        
        # Get user intent (for priority decisions)
        user_intent = state.get("user_intent", "")
        
        console.print("[cyan]Analyzing screen...[/cyan]")
        extracted_context = run_observer(screenshot_b64, user_intent)

        # Feature 2: Capture confirmation — user knows immediately what was captured
        content_type = extracted_context.get("content_type", "unknown")
        title = (extracted_context.get("title", "") or "untitled")[:50]
        confidence = extracted_context.get("confidence", 0.0)
        console.print(
            f"[green]Captured:[/green] {content_type} — {title} "
            f"[dim](confidence: {confidence:.2f})[/dim]"
        )

        # Feature 4: Confidence explanation — tell user WHY confidence is low before retrying
        if confidence < 0.6:
            reasons = []
            if not extracted_context.get("primary_text"):
                reasons.append("no text visible")
            if not extracted_context.get("title"):
                reasons.append("no title detected")
            if not reasons:
                reasons.append("screen may be blurry or partially visible")
            console.print(
                f"[yellow]Low confidence ({confidence:.2f}) — {', '.join(reasons)}. "
                "Retrying capture...[/yellow]"
            )

        # Feature 3: Content-type mismatch detection
        url = extracted_context.get("url_visible") or ""
        if url:
            if "youtube.com" in url and content_type != "youtube":
                console.print(
                    f"[yellow]Heads up: URL looks like YouTube but classified as '{content_type}'. "
                    "Try switching focus to the video tab.[/yellow]"
                )
            elif ("github.com" in url or "docs." in url) and content_type == "other":
                console.print(
                    f"[yellow]Heads up: URL looks like documentation but classified as 'other'. "
                    "The page may still be loading.[/yellow]"
                )

        return {
            "extracted_context": extracted_context,
            "error": None,
        }
    
    except Exception as e:
        # If Observer fails, set error and let error_node handle it
        return {
            "error": f"Observer failed: {str(e)}",
            "should_continue": False,
        }






def guide_node(state: ContextFlowState) -> dict:
    """Guide Agent: Generate actionable advice from Observer's context.

    Bug fix: parser now filters extracted_context before passing to Guide.
    This removes noise fields irrelevant to the content type.
    """
    try:
        extracted_context = state.get("extracted_context")
        if not extracted_context:
            return {
                "error": "guide_node: No extracted_context in state",
                "should_continue": False,
            }

        user_intent = state.get("user_intent", "")
        session_history = state.get("session_history", [])

        # Filter context to only relevant fields for this content type
        from src.utils.parser import parse_context
        filtered_context = parse_context(extracted_context)

        guidance = run_guide(filtered_context, user_intent, session_history)

        # Update session_history: store lightweight summary, NOT full context
        # Full extracted_context can be 5000+ tokens — storing 3 would overflow Groq free tier
        history_entry = {
            "content_type": extracted_context.get("content_type", "unknown"),
            "title": (extracted_context.get("title") or "")[:80],
            "url_visible": extracted_context.get("url_visible"),
            "confidence": extracted_context.get("confidence", 0.0),
            "capture_timestamp": state.get("capture_timestamp", ""),
        }
        updated_history = (session_history + [history_entry])[-3:]

        return {
            "guidance": guidance,
            "session_history": updated_history,
            "retry_count": 0,  # Reset after successful cycle
            "error": None,
        }

    except Exception as e:
        return {
            "error": f"Guide failed: {str(e)}",
            "should_continue": False,
        }



def output_node(state: ContextFlowState) -> dict:
    """Output Node: Display guidance and copy to clipboard.
    
    This node:
    - Reads guidance from state
    - Displays in beautiful CLI format (rich)
    - Copies context_package to clipboard
    - Asks user: Continue or Quit?
    - Increments loop_count
    
    Args:
        state: Current graph state with guidance field
    
    Returns:
        dict with should_continue and loop_count updated
    """
    try:
        # Get guidance from state
        guidance = state.get("guidance")
        if not guidance:
            return {
                "error": "output_node: No guidance in state",
                "should_continue": False,
            }
        
        # Get loop count
        loop_count = state.get("loop_count", 0) + 1
        
        # Display guidance
        display_guidance(guidance, loop_count)
        
        # Copy context package to clipboard
        context_package = guidance.get("context_package", "")
        if context_package:
            success = copy_to_clipboard(context_package)
            if success:
                # Feature 4: Preview how much was copied so user knows what to expect
                char_count = len(context_package)
                preview = context_package[:80].replace("\n", " ")
                console.print(f"[green]Copied {char_count} chars to clipboard.[/green]")
                console.print(f"[dim]Preview: {preview}...[/dim]")
                console.print("[cyan]Paste into ChatGPT, Claude, or Gemini.[/cyan]")
            else:
                console.print("[yellow]Could not copy to clipboard.[/yellow]")
                console.print("[dim]Install xclip (Linux) or check pbcopy (macOS)[/dim]")
        
        # Ask user: Continue or Quit?
        should_continue = prompt_continue()

        # Feature 5: Session summary on exit
        if not should_continue:
            session_history = state.get("session_history", [])
            if session_history:
                console.print()
                console.print("[bold cyan]Session Summary[/bold cyan]")
                console.print(f"  Total captures: {loop_count}")
                # Count content types seen
                type_counts: dict[str, int] = {}
                for past in session_history:
                    ct = past.get("content_type", "unknown")
                    type_counts[ct] = type_counts.get(ct, 0) + 1
                for ct, count in type_counts.items():
                    console.print(f"  {ct}: {count} capture(s)")
                # Last topic
                last = session_history[-1]
                last_title = (last.get("title") or "")[:60]
                if last_title:
                    console.print(f"  Last topic: {last_title}")

        return {
            "loop_count": loop_count,
            "should_continue": should_continue,
            "error": None,
        }
    
    except Exception as e:
        return {
            "error": f"Output failed: {str(e)}",
            "should_continue": False,
        }
