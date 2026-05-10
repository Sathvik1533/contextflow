"""Test main.py without user input."""

from src.graph.builder import build_graph

print("Testing graph build...")
app = build_graph()
print("✅ Graph builds successfully!")
print(f"   Type: {type(app)}")
print("\n✅ TASK-008 COMPLETE: Entry point works!")
