"""ContextFlow - Main Entry Point

Run this to start the ContextFlow system.

Usage:
    python src/main.py
"""

from dotenv import load_dotenv
from src.graph.builder import build_graph
from rich.console import Console

# Load environment variables
load_dotenv()

console = Console()


def main():
    """Main entry point for ContextFlow."""
    
    # Print welcome banner
    console.print("\n" + "="*70, style="bold cyan")
    console.print("  ContextFlow — AI Context Gathering Assistant", style="bold cyan")
    console.print("="*70 + "\n", style="bold cyan")
    
    console.print("🎯 What this does:", style="bold yellow")
    console.print("   1. Captures your screen")
    console.print("   2. AI analyzes what's visible")
    console.print("   3. Generates learning advice")
    console.print("   4. Copies context to clipboard")
    console.print("   5. You paste into ChatGPT/Claude/Gemini\n")
    
    # Ask for user intent
    console.print("📝 What are you trying to learn right now?", style="bold yellow")
    console.print("   (Press Enter to skip)\n")
    # Ask for user intent through code
    user_intent = input("   → ").strip()
    if not user_intent:
        user_intent = "general learning"
    
    console.print(f"\n✅ Got it! Helping you with: {user_intent}\n", style="green")
    
    # Build the graph
    console.print("🔧 Building ContextFlow graph...", style="yellow")
    app = build_graph()
    console.print("✅ Graph ready!\n", style="green")
    
    # Initial state
    initial_state = {
        "screenshot_b64": "",
        "capture_timestamp": "",
        "user_intent": user_intent,
        "session_history": [],
        "extracted_context": {},
        "terminal_context": {},
        "guidance": {},
        "error": None,
        "loop_count": 0,
        "should_continue": True,
    }
    
    # Run the graph
    console.print("🚀 Starting ContextFlow...\n", style="bold green")
    console.print("="*70 + "\n", style="cyan")
    
    try:
        result = app.invoke(initial_state)
        
        # Debug: Print the final state
        if result.get("error"):
            console.print(f"\n⚠️  Error occurred: {result.get('error')}", style="red")
        
        console.print("\n" + "="*70, style="cyan")
        console.print("✅ ContextFlow session complete!", style="bold green")
        console.print(f"   Total captures: {result.get('loop_count', 0)}", style="green")
        console.print("="*70 + "\n", style="cyan")
        
    except KeyboardInterrupt:
        console.print("\n\n⚠️  Interrupted by user. Exiting...", style="yellow")
    except Exception as e:
        console.print(f"\n\n❌ Error: {str(e)}", style="bold red")
        console.print("   Check your .env file and API keys.", style="red")


if __name__ == "__main__":
    main()
