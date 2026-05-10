# tasks.md — Milestone 1 Checklist

## Before You Touch Code

- [ ] Read the LangGraph quickstart (15 min): https://langchain-ai.github.io/langgraph/tutorials/introduction/
- [ ] Create Google AI Studio account: https://aistudio.google.com
- [ ] Generate API key. Store it. Don't lose it.
- [ ] Verify Gemini 2.0 Flash is available in your region (India = yes, available)

---

## Step 1: Python Environment

```bash
# Create project folder
mkdir contextflow && cd contextflow

# Create virtual environment (ALWAYS use venv, never global pip)
python3 -m venv .venv
source .venv/bin/activate

# Verify Python version (need 3.11+)
python --version
```

- [ ] Folder created
- [ ] Venv activated (you see `(.venv)` in terminal prompt)
- [ ] Python 3.11+ confirmed

---

## Step 2: Install Dependencies

```bash
pip install langgraph langchain-google-genai mss Pillow python-dotenv rich
```

Create `requirements.txt`:
```
langgraph
langchain-google-genai
mss
Pillow
python-dotenv
rich
```

- [ ] All packages installed without errors
- [ ] `pip list | grep langgraph` shows version

---

## Step 3: API Key Setup

Create `.env` file in project root:
```
GOOGLE_API_KEY=your_key_here
```

Create `.gitignore`:
```
.env
.venv/
__pycache__/
*.pyc
snapshots/
```

**Critical:** Never commit `.env`. Check `.gitignore` works before `git init`.

- [ ] `.env` created with real API key
- [ ] `.gitignore` has `.env` in it
- [ ] `cat .gitignore` confirms `.env` is listed

---

## Step 4: Test Gemini API (Before LangGraph)

Create `test_api.py`:
```python
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
response = llm.invoke("Say hello in one sentence.")
print(response.content)
```

Run: `python test_api.py`

- [ ] Script runs without auth error
- [ ] Terminal prints a sentence from Gemini
- [ ] If 403 error: API key wrong or quota region issue — fix before continuing

---

## Step 5: Test Screen Capture

Create `test_capture.py`:
```python
import mss
import base64
from PIL import Image
import io

def capture_screen():
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # 1 = primary monitor
        shot = sct.grab(monitor)
        
        # Convert to PIL Image
        img = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
        
        # Resize to reduce tokens (Vision API charges by image size)
        img = img.resize((1280, 800), Image.LANCZOS)
        
        # Encode to base64
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode()

b64 = capture_screen()
print(f"Captured. Base64 length: {len(b64)} chars")
# Save to file to verify visually
import base64 as b64lib
with open("test_screenshot.png", "wb") as f:
    f.write(b64lib.b64decode(b64))
print("Saved test_screenshot.png — open it to verify")
```

- [ ] Script runs
- [ ] `test_screenshot.png` exists and shows your screen
- [ ] Base64 string is non-empty

---

## Step 6: Build Observer Node (Core of Milestone 1)

Create `observer.py`:
```python
import json
import base64
import io
import mss
from PIL import Image
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

load_dotenv()

OBSERVER_PROMPT = """You are a screen analysis agent. Analyze this screenshot and respond ONLY with valid JSON.
No prose, no markdown, no explanation. JSON only.

Required schema:
{
  "content_type": "youtube or documentation or code or error or other",
  "title": "page or video title visible on screen",
  "primary_text": "main readable content, max 500 chars",
  "code_blocks": ["list of code strings visible"],
  "error_messages": ["list of error or stack trace strings"],
  "url_visible": "URL string or null",
  "confidence": 0.0
}

confidence = how certain you are about content_type (0.0 to 1.0)."""

def capture_screen() -> str:
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        shot = sct.grab(monitor)
        img = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
        img = img.resize((1280, 800), Image.LANCZOS)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode()

def run_observer(screenshot_b64: str) -> dict:
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    
    message = HumanMessage(content=[
        {"type": "text", "text": OBSERVER_PROMPT},
        {"type": "image_url", "image_url": f"data:image/png;base64,{screenshot_b64}"}
    ])
    
    response = llm.invoke([message])
    raw = response.content.strip()
    
    # Strip markdown code fences if Gemini adds them (it sometimes does)
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    
    return json.loads(raw)

if __name__ == "__main__":
    print("Capturing screen...")
    img = capture_screen()
    print("Sending to Gemini Vision...")
    result = run_observer(img)
    print("\n=== Observer Output ===")
    print(json.dumps(result, indent=2))
```

Run: `python observer.py`

- [ ] Script runs
- [ ] Terminal shows JSON output
- [ ] `content_type` field is populated
- [ ] No JSON parse errors
- [ ] `confidence` is a float between 0 and 1

---

## Step 7: Verify State Schema

Create `state.py`:
```python
from typing import TypedDict, Optional, List

class ContextFlowState(TypedDict):
    screenshot_b64: str
    capture_timestamp: str
    extracted_context: dict
    guidance: dict
    error: Optional[str]
    loop_count: int
    should_continue: bool
```

- [ ] File created
- [ ] Import works: `from state import ContextFlowState` in Python REPL without error

---

## Step 8: Milestone 1 Integration Test

Run `observer.py` against 3 different screens:

| Screen | Expected content_type | confidence > 0.7? |
|--------|----------------------|-------------------|
| YouTube video open | `youtube` | ☐ |
| LangChain docs page | `documentation` | ☐ |
| VS Code with code | `code` | ☐ |

- [ ] All 3 pass
- [ ] JSON is valid for all 3
- [ ] No API errors (if 429: wait 60s, retry)

---

## Milestone 1 Complete When:

1. `python observer.py` runs on any screen and returns valid JSON matching the schema
2. You understand what each line does (not just copy-paste)
3. `.env` is NOT committed to git
4. You can explain: "What is a LangGraph node and why is Observer a node?"

Move to Week 2 only after all 4 are true.

---

## Common Errors and Fixes

| Error | Fix |
|-------|-----|
| `google.auth.exceptions.DefaultCredentialsError` | `.env` not loaded. Add `load_dotenv()` before API call |
| `json.JSONDecodeError` | Gemini returned prose not JSON. Strengthen prompt: add "JSON ONLY, no backticks" |
| `mss.exception.ScreenShotError` | macOS Screen Recording permission not granted. System Prefs → Privacy → Screen Recording → add Terminal |
| `429 Resource Exhausted` | Hit rate limit. Add `time.sleep(5)` before retry |
| `PIL.Image` import error | `pip install Pillow` (capital P) |
