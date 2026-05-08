"""LangGraph node functions for ContextFlow.

Each node is a function that:
1. Receives the current state (ContextFlowState)
2. Does work (capture screen, call API, display output)
3. Returns a dict with updated fields to merge into state

LangGraph automatically merges the returned dict into the state.
"""

from src.capture.screen import capture_screen
from src.graph.state import ContextFlowState


def capture_node(state: ContextFlowState) -> dict:
    """Entry point: Capture the screen and write to state.
    
    This node:
    - Grabs the primary monitor using mss
    - Encodes to base64 PNG
    - Writes screenshot_b64 and capture_timestamp to state
    
    Args:
        state: Current graph state (not used in this node, but required by LangGraph)
    
    Returns:
        dict with screenshot_b64 and capture_timestamp keys
    
    Raises:
        mss.exception.ScreenShotError: If macOS Screen Recording permission denied
    """
    try:
        result = capture_screen(monitor_index=1, resize_to=(1280, 800))
        return {
            "screenshot_b64": result["screenshot_b64"],
            "capture_timestamp": result["capture_timestamp"],
            "error": None,  # Clear any previous errors
        }
    except Exception as e:
        # If capture fails, set error and let error_node handle it
        return {
            "error": f"Screen capture failed: {str(e)}",
            "should_continue": False,
        }
