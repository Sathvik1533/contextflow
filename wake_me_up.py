"""Wake up alarm - plays sound and shows notification after 5 minutes."""

import time
import os

print("⏰ ALARM SET FOR 5 MINUTES")
print("=" * 50)
print("Go take your break!")
print("I'll wake you up in 5 minutes...")
print("=" * 50)

# Wait 5 minutes (300 seconds)
time.sleep(300)

# Play system beep 5 times
print("\n🔔 WAKE UP! WAKE UP! WAKE UP!")
for i in range(5):
    os.system('afplay /System/Library/Sounds/Glass.aiff')
    time.sleep(1)

# Show macOS notification
os.system('''
osascript -e 'display notification "Time to build your Pizza Graph! 🍕" with title "⏰ WAKE UP!" sound name "Glass"'
''')

print("\n" * 3)
print("🚨" * 25)
print("⏰ TIME TO CODE!")
print("🚨" * 25)
print("\n")
print("💪 Let's build that Pizza Delivery Graph!")
print("🍕 You're going to create your first LangGraph!")
print("\n")
print("Say 'I'm back' in the chat when you're ready!")
