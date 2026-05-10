"""Practical demo: See how State flows through the graph.

This shows you EXACTLY what each node reads and writes.
Run this to understand the relay race with the notebook analogy.
"""

from src.graph.state import ContextFlowState

# Simulate what happens in the graph

print("="*70)
print("PRACTICAL DEMO: State Flow Through Nodes")
print("="*70)

# Initial state (empty notebook)
state: ContextFlowState = {
    "screenshot_b64": "",
    "capture_timestamp": "",
    "user_intent": "learning LangGraph",
    "session_history": [],
    "extracted_context": {},
    "guidance": {},
    "error": None,
    "loop_count": 0,
    "should_continue": True,
}

print("\n📋 INITIAL STATE (Empty Notebook):")
print(f"   screenshot_b64: '{state['screenshot_b64']}' (empty)")
print(f"   extracted_context: {state['extracted_context']} (empty)")
print(f"   guidance: {state['guidance']} (empty)")
print(f"   user_intent: '{state['user_intent']}'")

# Node 1: Capture
print("\n" + "="*70)
print("🏃 RUNNER 1: capture_node")
print("="*70)
print("What it does: Takes a screenshot")
print("What it reads from state: Nothing (it's the first runner)")
print("What it writes to state: screenshot_b64, capture_timestamp")

# Simulate capture_node
state["screenshot_b64"] = "iVBORw0KGgoAAAANS..." # Fake base64
state["capture_timestamp"] = "2026-05-10T13:30:00"

print(f"\n✅ After capture_node:")
print(f"   screenshot_b64: '{state['screenshot_b64'][:20]}...' (filled!)")
print(f"   capture_timestamp: '{state['capture_timestamp']}'")

# Node 2: Observer
print("\n" + "="*70)
print("🏃 RUNNER 2: observer_node")
print("="*70)
print("What it does: Analyzes the screenshot")
print("What it reads from state: screenshot_b64")
print("What it writes to state: extracted_context")

# Simulate observer_node
state["extracted_context"] = {
    "content_type": "documentation",
    "title": "LangGraph Tutorial",
    "primary_text": "LangGraph is a framework for building multi-agent systems...",
    "code_blocks": ["graph = StateGraph(MyState)"],
    "error_messages": [],
    "url_visible": "https://langchain.com/langgraph",
    "confidence": 0.85,
}

print(f"\n✅ After observer_node:")
print(f"   extracted_context:")
print(f"      content_type: '{state['extracted_context']['content_type']}'")
print(f"      title: '{state['extracted_context']['title']}'")
print(f"      confidence: {state['extracted_context']['confidence']}")

# Conditional Edge Decision
print("\n" + "="*70)
print("🔀 CONDITIONAL EDGE: should_retry_capture()")
print("="*70)
print(f"Checking: confidence >= 0.6?")
print(f"   confidence = {state['extracted_context']['confidence']}")
print(f"   0.85 >= 0.6? YES")
print(f"   Decision: Go to guide_node (continue)")

# Node 3: Guide
print("\n" + "="*70)
print("🏃 RUNNER 3: guide_node")
print("="*70)
print("What it does: Generates advice")
print("What it reads from state: extracted_context, user_intent")
print("What it writes to state: guidance")

# Simulate guide_node
state["guidance"] = {
    "summary": "You're reading LangGraph documentation about multi-agent systems.",
    "learning_path": [
        "Understand StateGraph basics",
        "Learn conditional edges",
        "Build your first graph",
    ],
    "questions_to_ask": [
        "How do conditional edges differ from regular edges?",
        "When should I use LangGraph vs manual orchestration?",
    ],
    "context_package": "=== ContextFlow Snapshot ===\n...",
}

print(f"\n✅ After guide_node:")
print(f"   guidance:")
print(f"      summary: '{state['guidance']['summary']}'")
print(f"      learning_path: {len(state['guidance']['learning_path'])} steps")

# Node 4: Output
print("\n" + "="*70)
print("🏃 RUNNER 4: output_node")
print("="*70)
print("What it does: Displays guidance, copies to clipboard, asks user")
print("What it reads from state: guidance")
print("What it writes to state: loop_count, should_continue")

# Simulate output_node
state["loop_count"] = 1
state["should_continue"] = False  # User said "quit"

print(f"\n✅ After output_node:")
print(f"   loop_count: {state['loop_count']}")
print(f"   should_continue: {state['should_continue']}")

# Conditional Edge Decision
print("\n" + "="*70)
print("🔀 CONDITIONAL EDGE: should_continue_loop()")
print("="*70)
print(f"Checking: should_continue == True?")
print(f"   should_continue = {state['should_continue']}")
print(f"   False == True? NO")
print(f"   Decision: Go to END (exit graph)")

# Final state
print("\n" + "="*70)
print("📋 FINAL STATE (Notebook After All Runners):")
print("="*70)
print(f"   screenshot_b64: ✅ Filled by capture_node")
print(f"   extracted_context: ✅ Filled by observer_node")
print(f"   guidance: ✅ Filled by guide_node")
print(f"   loop_count: {state['loop_count']} (incremented by output_node)")
print(f"   should_continue: {state['should_continue']} (set by output_node)")

print("\n" + "="*70)
print("🎯 KEY TAKEAWAY:")
print("="*70)
print("State is the NOTEBOOK passed between runners.")
print("Each runner (node) reads what it needs and writes its results.")
print("LangGraph automatically passes the notebook and makes routing decisions.")
print("="*70)
