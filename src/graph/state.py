"""LangGraph state schema for ContextFlow.

This TypedDict defines the shared state passed between all nodes in the graph.
Each node reads from and writes to this state object.
"""

from typing import Optional, TypedDict


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
    
    # --- Observer Layer (observer_node writes) ---
    extracted_context: dict
    """Structured JSON from Gemini Vision analysis.
    
    Schema:
    {
        "content_type": "youtube" | "documentation" | "code" | "error" | "other",
        "title": str,
        "primary_text": str,  # Max 500 chars
        "code_blocks": List[str],
        "error_messages": List[str],
        "url_visible": str | None,
        "confidence": float  # 0.0 to 1.0
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
    """Number of capture cycles completed. Increments after each output_node run."""
    
    should_continue: bool
    """False = exit graph. True = loop back to capture_node."""
