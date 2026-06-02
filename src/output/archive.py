"""Session Archive — Persistent storage for every ContextFlow capture.

TASK-018: Saves every session as a JSON file to ~/.contextflow/sessions/

WHY THIS EXISTS:
  Before this, every session was lost when ContextFlow closed.
  Now every capture is saved, tagged, and searchable.
  This eliminates Pain 2 (session reset), Pain 5 (dead screenshots),
  Pain 6 (I saw this somewhere), Pain 7 (Monday amnesia).

SECURITY:
  Raw screenshots are NEVER saved — only structured text.
  The session file contains meaning, not pixels.
"""

import json                          # PYTHON CONCEPT: importing a module
from datetime import datetime        # PYTHON CONCEPT: importing a specific class
from pathlib import Path             # PYTHON CONCEPT: importing Path for file handling
from typing import Optional          # PYTHON CONCEPT: type hints

from src.utils.logger import get_logger

logger = get_logger(__name__)

# PYTHON CONCEPT: variable — stores a path value
SESSIONS_DIR = Path.home() / ".contextflow" / "sessions"


def save_session(state: dict) -> Optional[Path]:
    """Save current capture to ~/.contextflow/sessions/ as JSON.

    PYTHON CONCEPT: function definition
      - Takes: state (a dictionary — the full ContextFlowState)
      - Returns: the file path where the session was saved (or None if failed)

    Logic:
      state dict → extract fields → build filename → create dir → write JSON → return path
    """
    try:
        # PYTHON CONCEPT: method call on a Path object
        # parents=True: also create parent folders if missing
        # exist_ok=True: don't crash if folder already exists
        SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

        # PYTHON CONCEPT: variable + string formatting
        # datetime.now() = current time
        # strftime = "string from time" — formats it into a readable string
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # PYTHON CONCEPT: f-string — builds a string using a variable inside {}
        filename = f"session_{timestamp}.json"

        # PYTHON CONCEPT: dictionary — key-value pairs storing session data
        # Note: screenshot_b64 is NOT here — security rule, never save pixels
        session_data = {
            "timestamp": timestamp,
            "content_type": state.get("extracted_context", {}).get("content_type", "unknown"),
            "title": state.get("extracted_context", {}).get("title", ""),
            "summary": state.get("guidance", {}).get("summary", ""),
            "url": state.get("extracted_context", {}).get("url_visible", ""),
            "branch": state.get("terminal_context", {}).get("git", {}).get("branch", ""),
            "user_level": state.get("user_level", "intermediate"),
            "confidence": state.get("extracted_context", {}).get("confidence", 0.0),
        }

        # PYTHON CONCEPT: Path / operator joins path parts
        file_path = SESSIONS_DIR / filename

        # PYTHON CONCEPT: method call — writes text to a file
        # json.dumps() converts a Python dictionary into a JSON string
        # indent=2 makes it human-readable with 2-space indentation
        file_path.write_text(json.dumps(session_data, indent=2), encoding="utf-8")

        logger.info("Session saved: %s", filename)

        # PYTHON CONCEPT: return statement — sends a value back to the caller
        return file_path

    except Exception:
        # PYTHON CONCEPT: exception handling — catches errors without crashing
        logger.exception("save_session failed — session not persisted")
        return None


def list_sessions() -> list[Path]:
    """Return all saved session files, newest first.

    PYTHON CONCEPT: function that returns a list
    PYTHON CONCEPT: list — ordered collection of items
    PYTHON CONCEPT: conditional — check if directory exists before reading it
    """
    # PYTHON CONCEPT: condition — only run if the folder exists
    if not SESSIONS_DIR.exists():
        return []   # PYTHON CONCEPT: return empty list as fallback

    # PYTHON CONCEPT: list() converts a generator to a list
    # glob("*.json") = find all files ending in .json
    # sorted() with key= reorders the list
    # reverse=True = newest files first
    sessions = sorted(
        list(SESSIONS_DIR.glob("*.json")),
        key=lambda p: p.stat().st_mtime,   # sort by modification time
        reverse=True,
    )
    return sessions


def load_session(file_path: Path) -> Optional[dict]:
    """Load a single session file and return its data as a dictionary.

    PYTHON CONCEPT: function that reads a file and returns a dictionary
    PYTHON CONCEPT: exception handling for file not found
    """
    try:
        # PYTHON CONCEPT: reading text from a file
        # json.loads() converts a JSON string back into a Python dictionary
        return json.loads(file_path.read_text(encoding="utf-8"))
    except Exception:
        logger.exception("load_session failed for %s", file_path)
        return None


def get_recent_sessions(n: int = 3) -> list[dict]:
    """Return the n most recent sessions as a list of dictionaries.

    PYTHON CONCEPT: function with a default parameter (n=3)
    PYTHON CONCEPT: loop — iterate through a list
    PYTHON CONCEPT: list building — collecting results
    """
    sessions = list_sessions()

    # PYTHON CONCEPT: list slicing — take only the first n items
    recent_files = sessions[:n]

    # PYTHON CONCEPT: loop — go through each file one by one
    results = []
    for file_path in recent_files:
        data = load_session(file_path)
        # PYTHON CONCEPT: condition — only add if data is valid
        if data:
            results.append(data)   # PYTHON CONCEPT: append adds to a list

    return results
