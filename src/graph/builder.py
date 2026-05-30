"""LangGraph StateGraph builder for ContextFlow.

This module assembles all nodes into an orchestrated workflow with:
- Automatic routing between nodes
- Conditional edges for intelligent decision-making
- Error handling
- Loop control

The graph structure:
    START → capture → observer → [confidence check] → guide → output → [continue check] → END
                         ↓                                        ↓
                    [if low confidence]                    [if should_continue]
                         ↓                                        ↓
                      capture ←────────────────────────────────────┘
"""

from langgraph.graph import StateGraph, END
from src.graph.state import ContextFlowState
from src.graph.nodes import capture_node, guide_node, memory_node, observer_node, output_node


MAX_RETRIES = 3  # Bug fix: prevent infinite low-confidence loop


def should_retry_capture(state: ContextFlowState) -> str:
    """Conditional edge: Check if Observer confidence is high enough.
    Bug fix: tracks retry_count to prevent infinite loop.
    After MAX_RETRIES low-confidence captures → exit with error message.

    Returns: "guide", "capture", or END
    """
    if state.get("error"):
        return END

    extracted_context = state.get("extracted_context", {})
    confidence = extracted_context.get("confidence", 0.0)

    if confidence >= 0.6:
        return "guide"

    # Low confidence — use retry_count (NOT loop_count) to prevent infinite loop
    # loop_count = completed cycles. retry_count = failed attempts this cycle.
    retry_count = state.get("retry_count", 0)
    if retry_count >= MAX_RETRIES:
        return END

    return "capture"


def should_continue_loop(state: ContextFlowState) -> str:
    """Conditional edge: Check if user wants to continue or quit.
    
    This routing function decides:
    - If should_continue = True → go to "capture" (loop again)
    - If should_continue = False → go to END (exit graph)
    
    The should_continue flag is set by output_node based on user input.
    
    Args:
        state: Current graph state with should_continue flag
    
    Returns:
        "capture" or END (next node name or terminal)
    """
    should_continue = state.get("should_continue", False)
    
    if should_continue:
        return "capture"  # User wants to continue → loop back
    else:
        return END  # User wants to quit → exit graph


def build_graph() -> StateGraph:
    """Build and compile the ContextFlow StateGraph.
    
    This function:
    1. Creates a StateGraph with ContextFlowState schema
    2. Adds all nodes (capture, observer, guide, output)
    3. Adds edges (automatic routing)
    4. Adds conditional edges (decision points)
    5. Sets entry point
    6. Compiles into runnable app
    
    Graph structure:
        START
          ↓
        capture_node (fills screenshot_b64)
          ↓
        observer_node (fills extracted_context)
          ↓
        [Decision: confidence >= 0.6?]
          ├─ YES → guide_node (fills guidance)
          └─ NO → capture_node (retry)
          ↓
        output_node (displays + clipboard)
          ↓
        [Decision: should_continue?]
          ├─ YES → capture_node (loop)
          └─ NO → END
    
    Returns:
        Compiled StateGraph app ready to invoke
    
    Example:
        >>> app = build_graph()
        >>> initial_state = {"loop_count": 0, "should_continue": True}
        >>> result = app.invoke(initial_state)
    """
    # Step 1: Create StateGraph with our state schema
    graph = StateGraph(ContextFlowState)
    # Step 2: Add nodes
    # Each node is a function that takes state and returns updated fields
    graph.add_node("capture", capture_node)
    graph.add_node("observer", observer_node)
    graph.add_node("memory", memory_node)   # TASK-013: memory between observer and guide
    graph.add_node("guide", guide_node)
    graph.add_node("output", output_node)

    # Step 3: Add edges (automatic routing)
    graph.add_edge("capture", "observer")  # After capture → always go to observer
    graph.add_edge("memory", "guide")      # After memory retrieval → always go to guide
    graph.add_edge("guide", "output")      # After guide → always go to output

    # Step 4: Add conditional edges (decision points)
    # These edges check state and decide which node to go to next
    # After observer → check confidence
    
    graph.add_conditional_edges(
        "observer",                    # Source node
        should_retry_capture,          # Routing function
        {
            "guide": "memory",         # TASK-013: high confidence → memory first, then guide
            "capture": "capture",      # low confidence → retry capture
            END: END,
        }
    )
    # After output → check should_continue
    graph.add_conditional_edges(
        "output",                      # Source node
        should_continue_loop,          # Routing function
        {
            "capture": "capture",      # If returns "capture" → loop back
            END: END,                  # If returns END → exit graph
        }
    )
    # Step 5: Set entry point
    # This is where the graph starts when you call app.invoke()
    graph.set_entry_point("capture")
    # Step 6: Compile the graph
    # This validates the graph structure and returns a runnable app
    app = graph.compile()
    return app
