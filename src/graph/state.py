"""LangGraph state schema for ContextFlow.

This TypedDict defines the shared state passed between all nodes in the graph.
Each node reads from and writes to this state object.
"""

from typing import List, Optional, TypedDict


class ContextFlowState(TypedDict):
    """Shared state for the ContextFlow multi-agent system.
    
    This is the "baton" passed between nodes in the LangGraph.
    Each node reads specific fields and writes back its results.
    """
    
    # --- Input Layer (capture_node writes) ---
    screenshot_b64: str
    """Base64-encoded PNG screenshot from mss capture."""
    
    capture_timestamp: str
    """ISO 8601 timestamp of when the screenshot was taken."""
    
    user_intent: str
    """What the user is trying to learn right now.
    
    Captured at session start via CLI prompt: "What are you trying to learn?"
    Can be empty string if user presses Enter to skip.
    Used by Guide to personalize responses.
    
    Examples:
    - "learning React hooks"
    - "debugging authentication error"
    - "understanding LangGraph state management"
    - "" (skipped)
    """
    
    session_history: List[dict]
    """Last 3 extracted_context dicts from previous captures.
    
    Allows Guide to see patterns across multiple screens:
    - User looked at 3 different auth tutorials → suggest comparison
    - Same error appeared twice → suggest deeper investigation
    - Jumping between unrelated topics → suggest focus
    
    Limited to 3 to avoid token bloat. Oldest entries are dropped.
    """
    
    # --- Observer Layer (observer_node writes) ---
    extracted_context: dict
    """Structured JSON from Observer Vision analysis.

    Schema:
    {
        "content_type": "youtube" | "documentation" | "code" | "error" | "other",
        "title": str,
        "primary_text": str,       # ALL visible body text, no length limit
        "headings": List[str],     # Every heading/section title visible
        "lists": List[str],        # Every bullet point or list item visible
        "code_blocks": List[str],  # Every code snippet, exact characters
        "error_messages": List[str],
        "url_visible": str | None,
        "tables": List[str],       # Each table row as pipe-separated string
        "confidence": float        # 0.0 to 1.0
    }
    """
    
    # --- Terminal Layer (capture_node writes — captured alongside screenshot) ---
    terminal_context: dict
    """Terminal history and error detection. Written by capture_node, not a separate node.

    Fallback: if no shell history file found (~/.zsh_history / ~/.bash_history),
    returns empty lists — never crashes, never blocks the pipeline.

    Schema:
    {
        "recent_commands": List[str],  # Last 20 commands (empty if no history)
        "errors_detected": List[str],  # Commands with error keywords
        "current_directory": str,      # cwd (always available)
        "shell_type": str              # "zsh", "bash", or "unknown"
    }
    """
    
    # --- Guide Layer (guide_node writes) ---
    guidance: dict
    """Pedagogical response from Guide agent.
    
    Schema:
    {
        "summary": str,  # 2-3 sentences
        "learning_path": List[str],  # 3 actionable steps
        "questions_to_ask": List[str],  # 2 suggested prompts for external LLMs
        "context_package": str  # Full formatted text for clipboard
    }
    """
    
    # --- Control Flow ---
    error: Optional[str]
    """Error message if any node fails. None if no error."""
    
    loop_count: int
    """Number of completed capture cycles. Increments after each output_node run."""

    retry_count: int
    """Number of low-confidence re-capture attempts in the current cycle.

    Separate from loop_count — loop_count tracks completed cycles,
    retry_count tracks failed attempts within one cycle.
    Reset to 0 after each successful guide_node run.
    Used by should_retry_capture to prevent infinite re-capture loop.
    """

    should_continue: bool
    """False = exit graph. True = loop back to capture_node."""
