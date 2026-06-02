"""Tests for TASK-018: Session Archive.

PYTHON CONCEPTS in these tests:
- Functions (def test_...)
- Dictionaries (SAMPLE_STATE)
- Conditions (assert, if)
- Loops (for session in sessions)
- Lists (list of sessions)
- Strings (checking filenames end with .json)
"""

import json
from pathlib import Path

import pytest

from src.output.archive import get_recent_sessions, list_sessions, load_session, save_session

# PYTHON CONCEPT: dictionary — a sample state to test with
SAMPLE_STATE = {
    "extracted_context": {
        "content_type": "code",
        "title": "LangGraph tutorial",
        "url_visible": "https://langchain.com/docs",
        "confidence": 0.91,
    },
    "guidance": {
        "summary": "User is learning LangGraph StateGraph.",
    },
    "terminal_context": {
        "git": {"branch": "feature/task-018-session-archive"},
    },
    "user_level": "intermediate",
}


class TestSaveSession:
    def test_save_creates_json_file(self, tmp_path, monkeypatch):
        """save_session() must create a .json file on disk."""
        monkeypatch.setattr("src.output.archive.SESSIONS_DIR", tmp_path / "sessions")

        result = save_session(SAMPLE_STATE)

        # PYTHON CONCEPT: condition — assert checks if something is true
        assert result is not None
        assert result.exists()
        assert result.suffix == ".json"   # file ends with .json

    def test_save_contains_correct_fields(self, tmp_path, monkeypatch):
        """Saved file must contain content_type, title, branch, user_level."""
        monkeypatch.setattr("src.output.archive.SESSIONS_DIR", tmp_path / "sessions")

        result = save_session(SAMPLE_STATE)

        # PYTHON CONCEPT: reading a file and parsing JSON into a dictionary
        data = json.loads(result.read_text())

        assert data["content_type"] == "code"
        assert data["title"] == "LangGraph tutorial"
        assert data["branch"] == "feature/task-018-session-archive"
        assert data["user_level"] == "intermediate"
        assert data["confidence"] == 0.91

    def test_save_does_not_store_screenshot(self, tmp_path, monkeypatch):
        """Security rule: screenshot_b64 must NEVER appear in saved files."""
        monkeypatch.setattr("src.output.archive.SESSIONS_DIR", tmp_path / "sessions")

        state_with_screenshot = {**SAMPLE_STATE, "screenshot_b64": "fake_base64_data"}
        result = save_session(state_with_screenshot)

        content = result.read_text()
        assert "screenshot_b64" not in content
        assert "fake_base64_data" not in content

    def test_save_handles_empty_state_gracefully(self, tmp_path, monkeypatch):
        """save_session() must not crash on empty or partial state."""
        monkeypatch.setattr("src.output.archive.SESSIONS_DIR", tmp_path / "sessions")

        result = save_session({})

        # PYTHON CONCEPT: condition — even with empty input, should return a path
        assert result is not None
        assert result.exists()

    def test_save_returns_none_on_permission_error(self, tmp_path, monkeypatch):
        """If saving fails, return None — never crash the pipeline."""
        # Point to a path that cannot be created
        monkeypatch.setattr(
            "src.output.archive.SESSIONS_DIR",
            Path("/root/no_permission/sessions")
        )

        result = save_session(SAMPLE_STATE)
        assert result is None


class TestListSessions:
    def test_returns_empty_list_when_no_sessions(self, tmp_path, monkeypatch):
        """list_sessions() returns [] when folder doesn't exist yet."""
        monkeypatch.setattr(
            "src.output.archive.SESSIONS_DIR",
            tmp_path / "nonexistent"
        )

        # PYTHON CONCEPT: function call that returns a list
        result = list_sessions()
        assert result == []   # PYTHON CONCEPT: empty list comparison

    def test_returns_json_files_only(self, tmp_path, monkeypatch):
        """list_sessions() returns only .json files, not .txt or others."""
        monkeypatch.setattr("src.output.archive.SESSIONS_DIR", tmp_path)

        # PYTHON CONCEPT: creating files using Path objects
        (tmp_path / "session_1.json").write_text("{}")
        (tmp_path / "session_2.json").write_text("{}")
        (tmp_path / "notes.txt").write_text("not a session")

        result = list_sessions()

        # PYTHON CONCEPT: list length
        assert len(result) == 2

        # PYTHON CONCEPT: loop — check every item in the list
        for path in result:
            assert path.suffix == ".json"


class TestGetRecentSessions:
    def test_returns_n_most_recent(self, tmp_path, monkeypatch):
        """get_recent_sessions(n=2) returns at most 2 sessions."""
        monkeypatch.setattr("src.output.archive.SESSIONS_DIR", tmp_path / "sessions")

        # Save 3 sessions
        for _ in range(3):
            save_session(SAMPLE_STATE)

        result = get_recent_sessions(n=2)

        # PYTHON CONCEPT: list length check
        assert len(result) <= 2

    def test_returns_dictionaries(self, tmp_path, monkeypatch):
        """Each item returned must be a dictionary."""
        monkeypatch.setattr("src.output.archive.SESSIONS_DIR", tmp_path / "sessions")

        save_session(SAMPLE_STATE)
        result = get_recent_sessions(n=1)

        assert len(result) == 1
        # PYTHON CONCEPT: type check — isinstance checks if something is a dict
        assert isinstance(result[0], dict)


class TestLoadSession:
    def test_load_returns_dictionary(self, tmp_path, monkeypatch):
        """load_session() reads a file and returns a Python dictionary."""
        monkeypatch.setattr("src.output.archive.SESSIONS_DIR", tmp_path / "sessions")

        saved = save_session(SAMPLE_STATE)
        data = load_session(saved)

        assert isinstance(data, dict)
        assert "content_type" in data

    def test_load_returns_none_for_missing_file(self):
        """load_session() returns None if file doesn't exist."""
        result = load_session(Path("/nonexistent/file.json"))
        assert result is None
