"""Demo script for video recording.

This shows ContextFlow analyzing different content types.

INSTRUCTIONS:
1. Open YouTube tutorial in browser
2. Run this script
3. It will capture and analyze
4. Show the beautiful output
5. Repeat for docs and errors
"""

import time
from dotenv import load_dotenv
from src.capture.screen import capture_screen
from src.agents.observer import run_observer
from src.agents.guide import run_guide
from src.output.cli import display_guidance, copy_to_clipboard
from rich.console import Console

load_dotenv()
console = Console()

def demo_flow(scenario_name: str):
    """Run one demo scenario."""
    console.print(f"\n{'='*70}", style="bold cyan")
    console.print(f"  ContextFlow Demo — {scenario_name}", style="bold cyan")
    console.print(f"{'='*70}\n", style="bold cyan")
    
    # Step 1: Capture
    console.print("[1/4] Capturing screen...", style="yellow")
    time.sleep(1)
    capture_result = capture_screen(monitor_index=1, resize_to=(1280, 800))
    screenshot_b64 = capture_result["screenshot_b64"]
    console.print("✓ Captured\n", style="green")
    
    # Step 2: Observer
    console.print("[2/4] Running Observer (Llama 4 Scout Vision)...", style="yellow")
    console.print("⏳ Analyzing screen...\n")
    extracted_context = run_observer(screenshot_b64)
    console.print(f"✓ Detected: {extracted_context['content_type']}", style="green")
    console.print(f"✓ Title: {extracted_context['title']}", style="green")
    console.print(f"✓ Confidence: {extracted_context['confidence']:.2f}\n", style="green")
    
    # Step 3: Guide
    console.print("[3/4] Running Guide (Llama 3.3 70B)...", style="yellow")
    console.print("⏳ Generating advice...\n")
    guidance = run_guide(extracted_context, user_intent="learning AI and building projects")
    console.print("✓ Guidance generated\n", style="green")
    
    # Step 4: Output
    console.print("[4/4] Displaying guidance...\n", style="yellow")
    display_guidance(guidance, loop_count=1)
    
    # Copy to clipboard
    context_package = guidance.get("context_package", "")
    if copy_to_clipboard(context_package):
        console.print("\n✅ Context package copied to clipboard!", style="bold green")
        console.print("   Paste it into ChatGPT, Claude, or Gemini.\n", style="green")
    
    console.print(f"\n{'='*70}\n", style="bold cyan")


if __name__ == "__main__":
    console.print("\n🚀 ContextFlow Demo (Loop Mode)\n", style="bold cyan")
    console.print("INSTRUCTIONS:", style="bold yellow")
    console.print("1. Open content in browser (YouTube, docs, website)")
    console.print("2. Press Enter to capture and analyze")
    console.print("3. Type 'q' to quit\n")
    
    while True:
        user_input = input("Press Enter to capture (or 'q' to quit): ").strip().lower()
        
        if user_input == 'q':
            console.print("\n👋 Goodbye!", style="bold cyan")
            break
        
        # Run demo
        demo_flow("Real-Time Analysis")
        
        console.print("\n" + "="*70 + "\n", style="bold cyan")
