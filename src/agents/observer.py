"""Observer Agent — Screen Analysis with Groq Vision API.

This agent receives a base64-encoded screenshot and returns structured JSON
describing what's on screen: content type, title, code, errors, etc.

The Observer's job: Turn pixels into structured data.

Model: meta-llama/llama-4-scout-17b-16e-instruct (Llama 4 Scout with vision)
"""

import json
import os
import re
from typing import Any

from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq


# Strict JSON-only prompt — no prose, no markdown, just JSON
OBSERVER_PROMPT = """You are a screen analysis agent. Analyze this screenshot and respond ONLY with valid JSON.

CRITICAL RULES:
- Output ONLY raw JSON, no markdown fences, no explanation, no prose
- Do NOT wrap in ```json or ``` 
- Follow the exact schema below

PRIORITY RULE (MOST IMPORTANT):
If the screenshot shows BOTH a browser/application window AND a terminal/IDE:
→ ANALYZE THE BROWSER/APPLICATION CONTENT, NOT THE TERMINAL
→ Ignore terminal windows, code editors, and development tools
→ Focus on the MAIN CONTENT the user is viewing (YouTube, websites, documentation pages)

Example: If you see a browser showing ESPN cricket + a terminal with Python code:
→ Analyze the ESPN cricket content (content_type: "other", title: "ESPN Cricket")
→ Do NOT analyze the terminal/Python code

SCHEMA (you MUST match this exactly):
{
  "content_type": "youtube" | "documentation" | "code" | "error" | "other",
  "title": "string — page/video title visible on screen",
  "primary_text": "string — main readable content, max 500 chars",
  "code_blocks": ["array of code strings visible on screen"],
  "error_messages": ["array of error/stack trace strings visible"],
  "url_visible": "string or null — any URL visible in browser/terminal",
  "confidence": 0.0-1.0 — how confident you are in this analysis
}

CONTENT TYPE DEFINITIONS:
- "youtube": YouTube video player visible
- "documentation": Technical docs, tutorials, blog posts, README files
- "code": IDE, code editor, terminal with code (ONLY if no browser/app visible)
- "error": Error messages, stack traces, red text, exception logs
- "other": Anything else (websites, sports pages, news, desktop, settings, blank screen)

CONFIDENCE SCORING:
- 0.9-1.0: Very clear, can read text easily
- 0.7-0.9: Mostly clear, some text readable
- 0.5-0.7: Somewhat unclear, hard to read details
- 0.0-0.5: Very unclear, blurry, or blank screen

Analyze the screenshot now. Output ONLY the JSON object."""


def run_observer(screenshot_b64: str) -> dict[str, Any]:
    """Run the Observer agent on a screenshot.
    
    This function:
    1. Sends screenshot to Groq Vision API (meta-llama/llama-4-scout-17b-16e-instruct)
    2. Receives response (might have markdown fences)
    3. Strips fences if present
    4. Parses JSON
    5. Validates schema
    
    Args:
        screenshot_b64: Base64-encoded PNG string
    
    Returns:
        dict matching the Observer schema:
        {
            "content_type": str,
            "title": str,
            "primary_text": str,
            "code_blocks": List[str],
            "error_messages": List[str],
            "url_visible": str | None,
            "confidence": float
        }
    
    Raises:
        ValueError: If API returns invalid JSON or missing required fields
        Exception: If API call fails
    """
    # Initialize Groq Vision model
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment")
    
    llm = ChatGroq(
        model="meta-llama/llama-4-scout-17b-16e-instruct",  # Updated: Llama 4 Scout with vision support
        api_key=api_key,
        temperature=0.1,  # Low temperature = more consistent JSON output
    )
    
    # Build the message with text prompt + image
    # Groq Vision expects: HumanMessage with content=[text_dict, image_dict]
    message = HumanMessage(
        content=[
            {"type": "text", "text": OBSERVER_PROMPT},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{screenshot_b64}"},
            },
        ]
    )
    
    # Call the API
    response = llm.invoke([message])
    raw_content = response.content
    
    # Strip markdown fences if present (API sometimes returns ```json...```)
    # Pattern: ```json\n{...}\n``` or ```{...}```
    cleaned = re.sub(r"^```(?:json)?\s*\n?", "", raw_content.strip())
    cleaned = re.sub(r"\n?```$", "", cleaned)
    
    # Parse JSON
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Observer returned invalid JSON. Raw response:\n{raw_content}\n\nError: {e}"
        )
    
    # Validate required fields
    required_fields = [
        "content_type",
        "title",
        "primary_text",
        "code_blocks",
        "error_messages",
        "url_visible",
        "confidence",
    ]
    missing = [field for field in required_fields if field not in data]
    if missing:
        raise ValueError(
            f"Observer JSON missing required fields: {missing}\n\nReceived: {data}"
        )
    
    # Validate content_type is one of the allowed values
    valid_types = ["youtube", "documentation", "code", "error", "other"]
    if data["content_type"] not in valid_types:
        raise ValueError(
            f"Invalid content_type: {data['content_type']}. Must be one of {valid_types}"
        )
    
    # Validate confidence is a float between 0 and 1
    if not isinstance(data["confidence"], (int, float)) or not (0 <= data["confidence"] <= 1):
        raise ValueError(
            f"Invalid confidence: {data['confidence']}. Must be float between 0.0 and 1.0"
        )
    
    return data
