"""Live test of Observer agent with real screenshot and Groq API.

This script:
1. Captures your current screen
2. Sends to Observer agent
3. Prints the extracted context

Run this to verify Observer works end-to-end.
"""

import json
from dotenv import load_dotenv
from src.capture.screen import capture_screen
from src.agents.observer import run_observer

# Load API key from .env
load_dotenv()

print("=" * 60)
print("OBSERVER LIVE TEST")
print("=" * 60)

# Step 1: Capture screen
print("\n[1/3] Capturing your screen...")
capture_result = capture_screen(monitor_index=1, resize_to=(1280, 800))
screenshot_b64 = capture_result["screenshot_b64"]
timestamp = capture_result["capture_timestamp"]
print(f"✓ Captured at {timestamp}")
print(f"✓ Screenshot size: {len(screenshot_b64)} characters (base64)")

# Step 2: Run Observer
print("\n[2/3] Sending to Groq Vision API (llama-3.2-11b-vision-preview)...")
print("⏳ This may take 5-10 seconds...")

try:
    extracted_context = run_observer(screenshot_b64)
    print("✓ Observer returned valid JSON")
    
    # Step 3: Display results
    print("\n[3/3] EXTRACTED CONTEXT:")
    print("=" * 60)
    print(json.dumps(extracted_context, indent=2))
    print("=" * 60)
    
    # Summary
    print(f"\n📊 SUMMARY:")
    print(f"   Content Type: {extracted_context['content_type']}")
    print(f"   Title: {extracted_context['title']}")
    print(f"   Confidence: {extracted_context['confidence']:.2f}")
    print(f"   Code Blocks: {len(extracted_context['code_blocks'])}")
    print(f"   Errors: {len(extracted_context['error_messages'])}")
    
    if extracted_context['confidence'] < 0.6:
        print("\n⚠️  WARNING: Low confidence! Observer is unsure about this screen.")
        print("   In the full graph, this would trigger a re-capture.")
    else:
        print("\n✅ SUCCESS! Observer confidence is good.")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nIf you see a rate limit error, wait 60 seconds and try again.")
    print("Groq free tier: 15 requests/minute")
