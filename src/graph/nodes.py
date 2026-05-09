"""LangGraph node functions for ContextFlow.

Each node is a function that:
1. Receives the current state (ContextFlowState)
2. Does work (capture screen, call API, display output)
3. Returns a dict with updated fields to merge into state

LangGraph automatically merges the returned dict into the state.
"""

from src.agents.guide import run_guide
from src.agents.observer import run_observer
from src.capture.screen import capture_screen
from src.graph.state import ContextFlowState
from src.output.cli import copy_to_clipboard, display_guidance, prompt_continue


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
    """Observer Agent: Analyze screenshot and extract structured context.
    
    This node:
    - Reads screenshot_b64 from state
    - Sends to Groq Vision API (meta-llama/llama-4-scout-17b-16e-instruct)
    - Parses response into structured JSON
    - Writes extracted_context to state
    
    If confidence < 0.6, the graph will trigger a re-capture via conditional edge.
    
    Args:
        state: Current graph state with screenshot_b64 field
    
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
        
        # Run the Observer agent
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



def guide_node(state: ContextFlowState) -> dict:
    """Guide Agent: Generate actionable advice from Observer's context.
    
    This node:
    - Reads extracted_context from state
    - Reads user_intent from state (optional)
    - Sends to Groq Text API (llama-3.3-70b-versatile)
    - Generates summary, learning path, questions, context package
    - Writes guidance to state
    
    Args:
        state: Current graph state with extracted_context field
    
    Returns:
        dict with guidance key (or error if API fails)
    """
    try:
        # Get extracted context from state
        extracted_context = state.get("extracted_context")
        if not extracted_context:
            return {
                "error": "guide_node: No extracted_context in state",
                "should_continue": False,
            }
        
        # Get user intent (optional)
        user_intent = state.get("user_intent", "")
        
        # Run the Guide agent
        guidance = run_guide(extracted_context, user_intent)
        
        return {
            "guidance": guidance,
            "error": None,  # Clear any previous errors
        }
    
    except Exception as e:
        # If Guide fails, set error and let error_node handle it
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
                print("✅ Context package copied to clipboard!")
                print("   Paste it into ChatGPT, Claude, or Gemini.")
            else:
                print("⚠️  Could not copy to clipboard (pbcopy not available)")
        
        # Ask user: Continue or Quit?
        should_continue = prompt_continue()
        
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
