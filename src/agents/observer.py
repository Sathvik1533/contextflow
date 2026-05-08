"""Observer Agent — Gemini Vision analysis of screenshots.

This agent is the "eyes" of ContextFlow. It receives a base64 screenshot
and returns structured JSON describing what's on screen.
"""

import json
import os

from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# Strict prompt to force JSON-only output
OBSERVER_PROMPT = """You are a screen analysis agent. Analyze this screenshot and respond ONLY with valid JSON.

CRITICAL RULES:
- NO prose, NO markdown, NO explanation
- NO code fences (no ```json or ```)
- ONLY raw JSON object
- If you cannot determine something, use null or empty array

Required JSON schema:
{
  "content_type": "youtube" | "documentation" | "code" | "error" | "other",
  "title": "page or video title visible on screen",
  "primary_text": "main readable content, max 500 chars",
  "code_blocks": ["list of code strings visible on screen"],
  "error_messages": ["list of error or stack trace strings"],
  "url_visible": "URL string if visible, otherwise null",
  "confidence": 0.85
}

confidence = how certain you are about content_type (0.0 to 1.0)

Examples:
- YouTube video → content_type: "youtube", extract video title
- Documentation page → content_type: "documentation", extract page heading
- Code editor → content_type: "code", extract visible code
- Error dialog → content_type: "error", extract error message
- Blank/unclear → content_type: "other", confidence < 0.6

Respond with JSON only. Start with { and end with }."""


def run_observer(screenshot_b64: str, api_key: str | None = None) -> dict:
    """Analyze a screenshot using Gemini Vision and return structured JSON.
    
    Args:
        screenshot_b64: Base64-encoded PNG screenshot
        api_key: Google AI Studio API key (if None, reads from GOOGLE_API_KEY env var)
    
    Returns:
        dict matching the Observer schema with keys:
            - content_type: str
            - title: str
            - primary_text: str
            - code_blocks: list[str]
            - error_messages: list[str]
            - url_visible: str | None
            - confidence: float
    
    Raises:
        ValueError: If API returns invalid JSON or missing required fields
        Exception: If API call fails (auth, rate limit, etc.)
    """
    # Initialize Gemini Vision model
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        google_api_key=api_key or os.getenv("GOOGLE_API_KEY"),
    )
    
    # Construct message with text prompt + image
    message = HumanMessage(
        content=[
            {"type": "text", "text": OBSERVER_PROMPT},
            {
                "type": "image_url",
                "image_url": f"data:image/png;base64,{screenshot_b64}",
            },
        ]
    )
    
    # Call Gemini Vision
    response = llm.invoke([message])
    raw_output = response.content.strip()
    
    # Strip markdown code fences if present (Gemini sometimes adds them)
    cleaned = _strip_markdown_fences(raw_output)
    
    # Parse JSON
    try:
        result = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Observer returned invalid JSON. Raw output: {raw_output[:200]}"
        ) from e
    
    # Validate required fields
    required_fields = ["content_type", "title", "confidence"]
    missing = [f for f in required_fields if f not in result]
    if missing:
        raise ValueError(f"Observer JSON missing required fields: {missing}")
    
    # Ensure confidence is a float
    if not isinstance(result["confidence"], (int, float)):
        raise ValueError(f"confidence must be a number, got: {result['confidence']}")
    
    return result


def _strip_markdown_fences(text: str) -> str:
    """Remove markdown code fences from text.
    
    Gemini sometimes wraps JSON in:
        ```json
        {...}
        ```
    
    This function strips those fences to get raw JSON.
    """
    text = text.strip()
    
    # Remove opening fence
    if text.startswith("```"):
        # Find the end of the first line (the fence line)
        first_newline = text.find("\n")
        if first_newline != -1:
            text = text[first_newline + 1 :]
    
    # Remove closing fence
    if text.endswith("```"):
        text = text[: -3]
    
    return text.strip()
