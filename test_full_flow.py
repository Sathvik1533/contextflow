"""Live test of Observer → Guide flow with real Groq API.

This script:
1. Captures your current screen
2. Sends to Observer agent
3. Sends Observer output to Guide agent
4. Prints the full guidance

Run this to verify the full flow works end-to-end.
"""

import json
from dotenv import load_dotenv
from src.capture.screen import capture_screen
from src.agents.observer import run_observer
from src.agents.guide import run_guide

# Load API key from .env
load_dotenv()

print("=" * 70)
print("FULL FLOW TEST: OBSERVER → GUIDE")
print("=" * 70)

# Step 1: Capture screen
print("\n[1/4] Capturing your screen...")
capture_result = capture_screen(monitor_index=1, resize_to=(1280, 800))
screenshot_b64 = capture_result["screenshot_b64"]
print(f"✓ Screenshot captured ({len(screenshot_b64)} chars)")

# Step 2: Run Observer
print("\n[2/4] Running Observer (Llama 4 Scout Vision)...")
print("⏳ This may take 5-10 seconds...")

try:
    extracted_context = run_observer(screenshot_b64)
    print("✓ Observer returned valid JSON")
    print(f"\n📊 OBSERVER OUTPUT:")
    print(f"   Content Type: {extracted_context['content_type']}")
    print(f"   Title: {extracted_context['title']}")
    print(f"   Confidence: {extracted_context['confidence']:.2f}")
    
except Exception as e:
    print(f"\n❌ Observer failed: {e}")
    exit(1)

# Step 3: Run Guide
print("\n[3/4] Running Guide (Llama 3.3 70B Text)...")
print("⏳ This may take 5-10 seconds...")

try:
    guidance = run_guide(
        extracted_context,
        user_intent="learning AI and building projects"
    )
    print("✓ Guide returned valid guidance")
    
except Exception as e:
    print(f"\n❌ Guide failed: {e}")
    exit(1)

# Step 4: Display results
print("\n[4/4] FULL GUIDANCE:")
print("=" * 70)
print(f"\n📝 SUMMARY:")
print(f"   {guidance['summary']}")

print(f"\n🎯 LEARNING PATH:")
for i, step in enumerate(guidance['learning_path'], 1):
    print(f"   {i}. {step}")

print(f"\n❓ QUESTIONS TO ASK:")
for i, question in enumerate(guidance['questions_to_ask'], 1):
    print(f"   {i}. {question}")

print(f"\n📋 CONTEXT PACKAGE (for clipboard):")
print("-" * 70)
print(guidance['context_package'])
print("-" * 70)

print("\n✅ SUCCESS! Full flow working: Capture → Observer → Guide")
print("\nNext: Add output_node to display this in CLI with rich")
