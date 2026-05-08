"""LangGraph node functions for ContextFlow.

Each node is a function that:
1. Receives the current state (ContextFlowState)
2. Does work (capture screen, call API, display output)
3. Returns a dict with updated fields to merge into state

LangGraph automatically merges the returned dict into the state.
"""

from src.agents.observer import run_observer
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



def observer_node(state: ContextFlowState) -> dict:
    """Analyze the screenshot using Gemini Vision.
    
    This node:
    - Reads screenshot_b64 from state
    - Calls Gemini Vision API via run_observer()
    - Writes extracted_context to state
    - If confidence < 0.6, could trigger re-capture (handled by edge logic)
    
    Args:
        state: Current graph state with screenshot_b64 populated
    
    Returns:
        dict with extracted_context key (or error if API fails)
    """
    try:
        screenshot_b64 = state["screenshot_b64"]
        
        # Call Gemini Vision
        extracted_context = run_observer(screenshot_b64)
        
        return {
            "extracted_context": extracted_context,
            "error": None,  # Clear any previous errors
        }
    
    except Exception as e:
        # If Observer fails, set error and let error_node handle it
        return {
            "error": f"Observer failed: {str(e)}",
            "should_continue": False,
        }
