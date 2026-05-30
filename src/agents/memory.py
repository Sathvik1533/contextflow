"""Memory Agent — ChromaDB persistent memory for ContextFlow.

TASK-013: This is what makes ContextFlow compound.
Without this, session 1 == session 100. With this, every capture
makes the next one smarter.

Flow:
  After observer_node → memory_node retrieves related past captures
  After guide_node   → memory_node stores the current capture

What it does:
  RETRIEVE: semantic search — "find the 3 past captures most similar to what's on screen now"
  STORE:    embed + save the current capture after each successful guide run
  DETECT:   patterns — same error N times, topic frequency, level signals

Storage: ~/.contextflow/chroma/ (local, persistent, no API cost)
Embeddings: chromadb's default (sentence-transformers, runs locally, free)
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from src.utils.logger import get_logger

logger = get_logger(__name__)

CHROMA_DIR = Path.home() / ".contextflow" / "chroma"


def _get_collection():
    """Get or create the ChromaDB collection.

    Lazy import so ChromaDB is only loaded when memory features are used.
    Falls back gracefully if chromadb is not installed.
    """
    try:
        import chromadb
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        return client.get_or_create_collection(
            name="contextflow_captures",
            metadata={"hnsw:space": "cosine"},
        )
    except ImportError:
        return None


def retrieve_memory(extracted_context: dict[str, Any]) -> dict[str, Any]:
    """Retrieve top 3 semantically related past captures.

    Called BEFORE guide_node runs so Guide receives memory context.

    What this injects into Guide:
    - past_captures: list of related past sessions
    - topic_count: how many times user has seen this topic
    - recurring_errors: same error patterns seen before
    - depth_signal: "seen 5x — go deeper than basics"

    Args:
        extracted_context: Current Observer output

    Returns:
        memory_context dict (empty structure if ChromaDB unavailable or no history)
    """
    empty = {
        "past_captures": [],
        "topic_count": 0,
        "recurring_errors": [],
        "depth_signal": "",
    }

    collection = _get_collection()
    if collection is None:
        return empty

    try:
        count = collection.count()
        if count == 0:
            return empty

        # Build query string from current screen content
        query_text = _build_query_text(extracted_context)
        if not query_text.strip():
            return empty

        n_results = min(3, count)
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        past_captures = []
        recurring_errors = []

        current_errors = set(extracted_context.get("error_messages", []))
        current_type = extracted_context.get("content_type", "")
        topic_count = 0

        for doc, meta, dist in zip(documents, metadatas, distances):
            similarity = 1.0 - dist  # cosine distance → similarity
            if similarity < 0.3:  # skip low-relevance results
                continue

            past_captures.append({
                "summary": doc[:300],
                "content_type": meta.get("content_type", ""),
                "title": meta.get("title", ""),
                "timestamp": meta.get("timestamp", ""),
                "similarity": round(similarity, 2),
            })

            # Count topic recurrence
            if meta.get("content_type") == current_type:
                topic_count += 1

            # Detect recurring error patterns
            past_errors = json.loads(meta.get("error_messages_json", "[]"))
            for err in past_errors:
                if any(curr in err or err in curr for curr in current_errors):
                    recurring_errors.append({
                        "error": err[:150],
                        "when": meta.get("timestamp", ""),
                    })

        # Build depth signal for Guide prompt
        depth_signal = _build_depth_signal(topic_count, past_captures)

        return {
            "past_captures": past_captures,
            "topic_count": topic_count,
            "recurring_errors": recurring_errors[:3],  # cap at 3
            "depth_signal": depth_signal,
        }

    except Exception:
        logger.exception("retrieve_memory failed — returning empty context")
        return empty


def store_capture(extracted_context: dict[str, Any], guidance: dict[str, Any]) -> bool:
    """Store the current capture in ChromaDB after a successful guide run.

    Called AFTER guide_node completes. Never blocks pipeline — silently fails.

    Args:
        extracted_context: Observer output for this capture
        guidance: Guide output for this capture

    Returns:
        True if stored successfully, False if failed silently
    """
    collection = _get_collection()
    if collection is None:
        return False

    try:
        # Build the document text (what gets embedded and searched later)
        document = _build_document_text(extracted_context, guidance)

        capture_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        metadata = {
            "content_type": extracted_context.get("content_type", "other"),
            "title": (extracted_context.get("title") or "")[:200],
            "url_visible": extracted_context.get("url_visible") or "",
            "confidence": float(extracted_context.get("confidence", 0.0)),
            "timestamp": timestamp,
            "error_messages_json": json.dumps(
                extracted_context.get("error_messages", [])[:5]
            ),
            "summary": (guidance.get("summary") or "")[:500],
        }

        collection.add(
            documents=[document],
            metadatas=[metadata],
            ids=[capture_id],
        )
        return True

    except Exception:
        logger.exception("store_capture failed — capture not persisted")
        return False


def _build_query_text(extracted_context: dict[str, Any]) -> str:
    """Build the text string used to query ChromaDB.

    Combines the most identifying fields from the current screen.
    Richer query = better semantic matches.
    """
    parts = []

    title = extracted_context.get("title") or ""
    if title:
        parts.append(title)

    primary_text = extracted_context.get("primary_text") or ""
    if primary_text:
        parts.append(primary_text[:500])

    error_messages = extracted_context.get("error_messages") or []
    if error_messages:
        parts.extend(error_messages[:3])

    code_blocks = extracted_context.get("code_blocks") or []
    if code_blocks:
        parts.append(code_blocks[0][:200])

    return " ".join(parts)


def _build_document_text(extracted_context: dict[str, Any], guidance: dict[str, Any]) -> str:
    """Build the full document text stored in ChromaDB.

    This is what gets embedded and retrieved. More detail = better retrieval.
    """
    parts = [
        f"CONTENT TYPE: {extracted_context.get('content_type', 'other')}",
        f"TITLE: {extracted_context.get('title') or 'Unknown'}",
        f"URL: {extracted_context.get('url_visible') or 'None'}",
    ]

    primary_text = extracted_context.get("primary_text") or ""
    if primary_text:
        parts.append(f"SCREEN TEXT: {primary_text[:800]}")

    errors = extracted_context.get("error_messages") or []
    if errors:
        parts.append(f"ERRORS: {' | '.join(errors[:5])}")

    code = extracted_context.get("code_blocks") or []
    if code:
        parts.append(f"CODE: {code[0][:300]}")

    summary = guidance.get("summary") or ""
    if summary:
        parts.append(f"GUIDE SUMMARY: {summary}")

    learning_path = guidance.get("learning_path") or []
    if learning_path:
        parts.append(f"LEARNING PATH: {' | '.join(learning_path[:3])}")

    return "\n".join(parts)


def _build_depth_signal(topic_count: int, past_captures: list[dict]) -> str:
    """Build a natural language signal for the Guide prompt.

    Tells Guide how deeply to explain based on repetition history.

    Examples:
      "First time on this topic — start with fundamentals."
      "Seen 3 times before — skip basics, go to patterns."
      "Seen 8+ times — focus on edge cases and architecture."
    """
    if topic_count == 0 and not past_captures:
        return "First time on this topic — start with fundamentals."
    elif topic_count <= 2:
        return f"Seen similar content {topic_count} time(s) — brief foundations, then practical."
    elif topic_count <= 5:
        return f"Seen this topic {topic_count} times — skip basics, focus on patterns and gotchas."
    else:
        return f"Deep familiarity ({topic_count} sessions) — focus on edge cases, architecture, and what most people miss."


def format_memory_for_guide(memory_context: dict[str, Any]) -> str:
    """Format memory_context into a string for injection into Guide prompt.

    Called inside guide_node to append memory to the prompt.
    Returns empty string if no relevant memory.
    """
    if not memory_context:
        return ""

    parts = []

    depth_signal = memory_context.get("depth_signal", "")
    if depth_signal:
        parts.append(f"MEMORY DEPTH SIGNAL: {depth_signal}")

    past_captures = memory_context.get("past_captures", [])
    if past_captures:
        parts.append("\nRELATED PAST CAPTURES:")
        for i, cap in enumerate(past_captures[:3], 1):
            title = cap.get("title") or "untitled"
            when = cap.get("timestamp", "")[:10]
            summary = cap.get("summary", "")[:150]
            sim = cap.get("similarity", 0.0)
            parts.append(f"  {i}. [{when}] {title} (relevance: {sim:.0%})\n     {summary}")

    recurring_errors = memory_context.get("recurring_errors", [])
    if recurring_errors:
        parts.append("\nRECURRING ERROR PATTERNS (seen before):")
        for err in recurring_errors[:3]:
            when = err.get("when", "")[:10]
            error_text = err.get("error", "")[:100]
            parts.append(f"  - [{when}] {error_text}")

    return "\n".join(parts)
