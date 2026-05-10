"""Test full flow with output display.

This shows what the user will see in the final product.
"""

from dotenv import load_dotenv
from src.capture.screen import capture_screen
from src.agents.observer import run_observer
from src.agents.guide import run_guide
from src.output.cli import display_guidance, copy_to_clipboard

load_dotenv()

print("\n🚀 ContextFlow Demo — Full Flow\n")

# Step 1: Capture
print("[1/4] Capturing screen...")
capture_result = capture_screen(monitor_index=1, resize_to=(1280, 800))
screenshot_b64 = capture_result["screenshot_b64"]
print("✓ Captured\n")

# Step 2: Observer
print("[2/4] Running Observer...")
extracted_context = run_observer(screenshot_b64)
print(f"✓ Detected: {extracted_context['content_type']}\n")

# Step 3: Guide
print("[3/4] Running Guide...")
guidance = run_guide(extracted_context, user_intent="learning AI and building projects")
print("✓ Guidance generated\n")

# Step 4: Output
print("[4/4] Displaying output...\n")
display_guidance(guidance, loop_count=1)

# Copy to clipboard
context_package = guidance.get("context_package", "")
if copy_to_clipboard(context_package):
    print("\n✅ Context package copied to clipboard!")
    print("   Paste it into ChatGPT, Claude, or Gemini.")
else:
    print("\n⚠️  Could not copy to clipboard")

print("\n🎉 Full flow complete!")
print("\nNext: Integrate into LangGraph with all nodes connected")
