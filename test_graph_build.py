"""Quick test to verify the graph builds without errors."""

from src.graph.builder import build_graph

if __name__ == "__main__":
    print("Building ContextFlow graph...")
    app = build_graph()
    print("✅ Graph built successfully!")
    print(f"   Type: {type(app)}")
    print("\nGraph structure:")
    print("  START → capture → observer → [confidence check] → guide → output → [continue check] → END")
    print("\nConditional edges:")
    print("  • observer → guide (if confidence >= 0.6)")
    print("  • observer → capture (if confidence < 0.6, retry)")
    print("  • output → capture (if should_continue = True, loop)")
    print("  • output → END (if should_continue = False, exit)")
