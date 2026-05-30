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

from src.utils.logger import get_logger

logger = get_logger(__name__)


# Base prompt — user_intent is injected dynamically in run_observer()
OBSERVER_PROMPT_TEMPLATE = """You are a screen extraction agent. Your job is to extract ALL visible text and structure from this screenshot with maximum accuracy.

CRITICAL RULES:
- Output ONLY raw JSON. No markdown fences. No explanation. No prose.
- Do NOT wrap in ```json or ```
- Extract what you SEE — do not summarize, do not paraphrase
- If a field has nothing visible, use empty string "" or empty array []

PRIORITY RULE:
If browser/app window AND terminal are both visible → analyze the BROWSER/APP content, ignore terminal.
{user_intent_instruction}

SCHEMA (match exactly):
{{
  "content_type": "youtube" | "documentation" | "code" | "error" | "other",
  "title": "exact title text visible on screen",
  "primary_text": "ALL visible body text — extract every word you can read, no length limit",
  "headings": ["every heading or section title visible, in order"],
  "lists": ["every bullet point, numbered item, or list item visible"],
  "code_blocks": ["every code snippet visible — exact characters, preserve indentation"],
  "error_messages": ["every error, warning, stack trace, or red text visible"],
  "url_visible": "exact URL from browser bar or null if none visible",
  "tables": ["each table row as a string, pipe-separated columns"],
  "confidence": 0.0
}}

CONTENT TYPE DEFINITIONS:
- "youtube": YouTube video player visible
- "documentation": Docs, tutorials, blog posts, README, guides
- "code": IDE, code editor, terminal with code
- "error": Error messages, stack traces, red text, exception logs dominant
- "other": Desktop, settings, forms, anything else

CONFIDENCE SCORING:
- 0.9-1.0: Text clearly readable
- 0.7-0.9: Mostly readable
- 0.5-0.7: Partially readable
- 0.0-0.5: Blurry, blank, or unreadable

Extract everything visible now. Output ONLY the JSON object."""


def run_observer(screenshot_b64: str, user_intent: str = "") -> dict[str, Any]:
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

    # Fallback chain: primary model → backup model
    # If primary is deprecated or fails, backup takes over automatically
    VISION_MODELS = [
        "meta-llama/llama-4-scout-17b-16e-instruct",      # primary — Llama 4 Scout
        "meta-llama/llama-4-maverick-17b-128e-instruct",  # backup — Llama 4 Maverick
    ]

    llm = None
    last_error = None
    for model in VISION_MODELS:
        try:
            llm = ChatGroq(model=model, api_key=api_key, temperature=0.1, timeout=30)
            break  # primary worked → stop trying
        except Exception as e:
            last_error = e
            continue  # try next model

    if llm is None:
        raise ValueError(f"All vision models failed. Last error: {last_error}")

    # Inject user_intent into prompt so Observer prioritizes what user is learning
    if user_intent:
        user_intent_instruction = f"USER INTENT: The user is trying to '{user_intent}'. Prioritize extracting content relevant to this."
    else:
        user_intent_instruction = ""

    prompt = OBSERVER_PROMPT_TEMPLATE.format(
        user_intent_instruction=user_intent_instruction
    )

    # Build the message with text prompt + image
    # Groq Vision expects: HumanMessage with content=[text_dict, image_dict]
    message = HumanMessage(
        content=[
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{screenshot_b64}"},
            },
        ]
    )
    
    # Call Groq Vision API with exponential backoff on rate limits (TASK-A)
    from src.utils.retry import retry_with_backoff
    response = retry_with_backoff(
        fn=lambda: llm.invoke([message]),
        max_attempts=3,
        base_delay=2.0,
        label="Observer Vision API",
    )
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
        "headings",
        "lists",
        "code_blocks",
        "error_messages",
        "url_visible",
        "tables",
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
