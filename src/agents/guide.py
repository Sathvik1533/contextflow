"""Guide Agent — Pedagogical Advice with Groq Text API.

This agent receives structured context from Observer and generates actionable
advice: summary, learning path, questions to ask, and a context package for
pasting into external LLMs.

The Guide's job: Turn observations into actionable advice.

Model: meta-llama/llama-3.3-70b-versatile (text reasoning, NOT vision)
"""

import os
import time
from typing import Any

from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq


# Content-type-specific prompts
GUIDE_PROMPTS = {
    "youtube": """You are a learning guide. A user is watching a YouTube video.

Screen context:
{context}

User intent: {user_intent}

Provide actionable advice in this EXACT format:

SUMMARY: (2-3 sentences describing what's on screen)

LEARNING PATH:
1. (First actionable step - e.g., "Pause at timestamp X")
2. (Second step - e.g., "Open related documentation")
3. (Third step - e.g., "Try this code example")

QUESTIONS TO ASK:
1. (First follow-up question for external LLMs)
2. (Second follow-up question for external LLMs)

Keep it concise and actionable.""",

    "code": """You are a code learning guide. A user is looking at code.

Screen context:
{context}

User intent: {user_intent}

Provide actionable advice in this EXACT format:

SUMMARY: (2-3 sentences: what this code does, key patterns used)

LEARNING PATH:
1. (First step - e.g., "Understand the main function")
2. (Second step - e.g., "Look up the X pattern")
3. (Third step - e.g., "Try modifying Y")

QUESTIONS TO ASK:
1. (First question to deepen understanding)
2. (Second question about related concepts)

Keep it concise and actionable.""",

    "error": """You are a debugging guide. A user is seeing an error.

Screen context:
{context}

User intent: {user_intent}

Provide actionable advice in this EXACT format:

SUMMARY: (2-3 sentences: what the error means, common causes)

LEARNING PATH:
1. (First debugging step)
2. (Second debugging step)
3. (Third debugging step or prevention tip)

QUESTIONS TO ASK:
1. (Question to understand the error better)
2. (Question about related debugging techniques)

Keep it concise and actionable.""",

    "documentation": """You are a documentation guide. A user is reading technical docs.

Screen context:
{context}

User intent: {user_intent}

Provide actionable advice in this EXACT format:

SUMMARY: (2-3 sentences: key concepts explained in these docs)

LEARNING PATH:
1. (First step - e.g., "Focus on section X")
2. (Second step - e.g., "Check related docs on Y")
3. (Third step - e.g., "Try this practical example")

QUESTIONS TO ASK:
1. (Question to deepen understanding)
2. (Question about practical application)

Keep it concise and actionable.""",

    "other": """You are a general learning guide. A user is looking at something on their screen.

Screen context:
{context}

User intent: {user_intent}

Provide actionable advice in this EXACT format:

SUMMARY: (2-3 sentences describing what's on screen)

LEARNING PATH:
1. (First actionable step based on visible content)
2. (Second step)
3. (Third step)

QUESTIONS TO ASK:
1. (First relevant question for external LLMs)
2. (Second relevant question)

Keep it concise and actionable.""",
}


def run_guide(
    extracted_context: dict[str, Any],
    user_intent: str = "",
    session_history: list[dict] | None = None,
    user_level: str = "intermediate",
    memory_str: str = "",
) -> dict[str, Any]:
    """Run the Guide agent on extracted context from Observer.
    
    This function:
    1. Selects prompt based on content_type
    2. Formats context into readable string
    3. Sends to Groq Text API (llama-3.3-70b-versatile)
    4. Parses response into structured guidance
    5. Builds context package for clipboard
    
    Args:
        extracted_context: Dict from Observer with keys:
            - content_type: str
            - title: str
            - primary_text: str
            - code_blocks: List[str]
            - error_messages: List[str]
            - url_visible: str | None
            - confidence: float
        user_intent: What user is trying to learn (optional)
    
    Returns:
        dict with keys:
            - summary: str
            - learning_path: List[str]
            - questions_to_ask: List[str]
            - context_package: str (formatted for clipboard)
    
    Raises:
        ValueError: If content_type is invalid
        Exception: If API call fails
    """
    # Get content type
    content_type = extracted_context.get("content_type", "other")
    
    # Validate content type
    if content_type not in GUIDE_PROMPTS:
        content_type = "other"
    
    # Format context for prompt
    context_str = f"""
Content Type: {content_type}
Title: {extracted_context.get('title', 'Unknown')}
URL: {extracted_context.get('url_visible', 'None')}

Main Content:
{extracted_context.get('primary_text', 'No text visible')}

Code Visible:
{chr(10).join(extracted_context.get('code_blocks', [])) or 'No code visible'}

Errors Detected:
{chr(10).join(extracted_context.get('error_messages', [])) or 'No errors detected'}

Confidence: {extracted_context.get('confidence', 0.0):.2f}
""".strip()
    
    # Build session history string for multi-turn context awareness
    history_str = ""
    if session_history:
        history_lines = []
        for i, past in enumerate(session_history[-3:], 1):  # max 3 past captures
            past_type = past.get("content_type", "unknown")
            past_title = (past.get("title", "") or "untitled")[:60]
            history_lines.append(f"  Capture {i}: {past_type} — {past_title}")
        history_str = "\nPREVIOUS CAPTURES (for context):\n" + "\n".join(history_lines)

    # Get prompt template
    prompt_template = GUIDE_PROMPTS[content_type]

    # Append memory context if available (TASK-013)
    memory_section = f"\n\n{memory_str}" if memory_str else ""

    # Fill in template
    prompt = prompt_template.format(
        context=context_str + history_str + memory_section,
        user_intent=user_intent or "Not specified"
    )
    
    # Initialize Groq Text model with fallback chain (mirrors observer.py pattern)
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment")

    TEXT_MODELS = [
        "llama-3.3-70b-versatile",   # primary — best reasoning
        "llama3-70b-8192",           # backup — older but stable
    ]

    llm = None
    last_error = None
    for model in TEXT_MODELS:
        try:
            llm = ChatGroq(model=model, api_key=api_key, temperature=0.3, timeout=30)
            break
        except Exception as e:
            last_error = e
            continue

    if llm is None:
        raise ValueError(f"All text models failed. Last error: {last_error}")
    
    # Call Groq Text API with exponential backoff on rate limits (TASK-A)
    from src.utils.retry import retry_with_backoff
    message = HumanMessage(content=prompt)
    response = retry_with_backoff(
        fn=lambda: llm.invoke([message]),
        max_attempts=3,
        base_delay=2.0,
        label="Guide Text API",
    )
    raw_content = response.content
    
    # Parse response
    guidance = _parse_guide_response(raw_content)
    
    # Build context package — includes Intent Layer for LLM clarity
    context_package = _build_context_package(extracted_context, guidance, user_intent, user_level)
    guidance["context_package"] = context_package
    
    return guidance


def _parse_guide_response(raw_content: str) -> dict[str, Any]:
    """Parse Guide's response into structured format.
    
    Expected format:
    SUMMARY: ...
    
    LEARNING PATH:
    1. ...
    2. ...
    3. ...
    
    QUESTIONS TO ASK:
    1. ...
    2. ...
    """
    lines = raw_content.strip().split("\n")
    
    summary = ""
    learning_path = []
    questions = []
    
    current_section = None
    
    for line in lines:
        line = line.strip()
        
        if line.startswith("SUMMARY:"):
            current_section = "summary"
            summary = line.replace("SUMMARY:", "").strip()
        elif line.startswith("LEARNING PATH:"):
            current_section = "learning_path"
        elif line.startswith("QUESTIONS TO ASK:"):
            current_section = "questions"
        elif line and current_section:
            # Remove numbering (1., 2., etc.)
            clean_line = line.lstrip("0123456789.-) ").strip()
            
            if current_section == "summary" and not summary:
                summary = clean_line
            elif current_section == "summary":
                summary += " " + clean_line
            elif current_section == "learning_path" and clean_line:
                learning_path.append(clean_line)
            elif current_section == "questions" and clean_line:
                questions.append(clean_line)
    
    return {
        "summary": summary or "No summary available",
        "learning_path": learning_path or ["Continue exploring"],
        "questions_to_ask": questions or ["What should I learn next?"],
    }


def _build_context_package(
    extracted_context: dict[str, Any],
    guidance: dict[str, Any],
    user_intent: str = "",
    user_level: str = "intermediate",
) -> str:
    """Build the context package string for clipboard.

    This is what gets copied to clipboard and pasted into ChatGPT/Claude/Gemini.
    Includes Intent Layer at the bottom so the LLM knows exactly what the user needs —
    not just what's on screen, but what kind of help is required.
    """
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Intent layer — closes the gap between "what's on screen" and "what user needs"
    intent_line = user_intent if user_intent and user_intent != "general learning" else "not specified"

    package = f"""=== ContextFlow Snapshot — {timestamp} ===
CONTENT TYPE: {extracted_context.get('content_type', 'unknown')}
TITLE: {extracted_context.get('title', 'Unknown')}
URL: {extracted_context.get('url_visible', 'None')}

WHAT'S ON SCREEN:
{extracted_context.get('primary_text', 'No text visible')}

CODE VISIBLE:
{chr(10).join(extracted_context.get('code_blocks', [])) or 'No code visible'}

ERRORS DETECTED:
{chr(10).join(extracted_context.get('error_messages', [])) or 'No errors detected'}

SUGGESTED QUESTIONS FOR LLMs:
{chr(10).join(f"{i+1}. {q}" for i, q in enumerate(guidance.get('questions_to_ask', [])))}

=== WHAT I NEED FROM YOU ===
My level: {user_level}
Specific question: {intent_line}
Preferred response: use examples from the actual content above, not generic examples
=== END SNAPSHOT ==="""
    
    return package
