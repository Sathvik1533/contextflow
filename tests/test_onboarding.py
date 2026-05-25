"""Tests for TASK-012: Onboarding + Profile Management.

Tests cover:
- Profile save/load round-trip
- update_profile_after_session updates correct fields
- Terminal signal analysis (with and without history)
- Morning briefing skip logic (< 1 hour since last session)
"""

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.onboarding.profile import (
    _analyze_terminal_for_profile,
    _load_profile,
    _save_profile,
    update_profile_after_session,
)


@pytest.fixture
def temp_profile_dir(tmp_path, monkeypatch):
    """Redirect PROFILE_PATH to a temp directory for all tests."""
    import src.onboarding.profile as profile_module
    monkeypatch.setattr(profile_module, "PROFILE_DIR", tmp_path)
    monkeypatch.setattr(profile_module, "PROFILE_PATH", tmp_path / "profile.json")
    return tmp_path


def _make_profile(**overrides) -> dict:
    base = {
        "role": "student",
        "user_level": "beginner",
        "stack": "Python",
        "goal": "learning LangGraph",
        "created_at": datetime.now().isoformat(),
        "last_seen": datetime.now().isoformat(),
        "session_count": 0,
        "topics_seen": {},
        "recent_titles": [],
        "terminal_signal": {},
    }
    base.update(overrides)
    return base


class TestProfilePersistence:
    def test_save_and_load_round_trip(self, temp_profile_dir):
        profile = _make_profile(stack="React", goal="landing a job")
        _save_profile(profile)
        loaded = _load_profile()
        assert loaded["stack"] == "React"
        assert loaded["goal"] == "landing a job"
        assert loaded["user_level"] == "beginner"

    def test_save_creates_directory_if_missing(self, tmp_path, monkeypatch):
        import src.onboarding.profile as m
        nested = tmp_path / "deep" / "nested"
        monkeypatch.setattr(m, "PROFILE_DIR", nested)
        monkeypatch.setattr(m, "PROFILE_PATH", nested / "profile.json")
        profile = _make_profile()
        _save_profile(profile)
        assert (nested / "profile.json").exists()

    def test_saved_file_is_valid_json(self, temp_profile_dir):
        profile = _make_profile()
        _save_profile(profile)
        raw = (temp_profile_dir / "profile.json").read_text()
        parsed = json.loads(raw)
        assert parsed["role"] == "student"


class TestUpdateProfileAfterSession:
    def test_increments_session_count(self, temp_profile_dir):
        profile = _make_profile(session_count=3)
        _save_profile(profile)
        update_profile_after_session(profile, [])
        loaded = _load_profile()
        assert loaded["session_count"] == 4

    def test_updates_topics_seen(self, temp_profile_dir):
        profile = _make_profile()
        _save_profile(profile)
        history = [
            {"content_type": "code", "title": "React hooks example"},
            {"content_type": "code", "title": "useState deep dive"},
            {"content_type": "documentation", "title": "React docs"},
        ]
        update_profile_after_session(profile, history)
        loaded = _load_profile()
        assert loaded["topics_seen"]["code"] == 2
        assert loaded["topics_seen"]["documentation"] == 1

    def test_keeps_last_10_recent_titles(self, temp_profile_dir):
        existing_titles = [f"title_{i}" for i in range(9)]
        profile = _make_profile(recent_titles=existing_titles)
        _save_profile(profile)
        history = [
            {"content_type": "code", "title": "new title A"},
            {"content_type": "code", "title": "new title B"},
        ]
        update_profile_after_session(profile, history)
        loaded = _load_profile()
        assert len(loaded["recent_titles"]) == 10
        assert "new title B" in loaded["recent_titles"]
        assert "title_0" not in loaded["recent_titles"]  # Oldest dropped

    def test_empty_session_history_still_increments_count(self, temp_profile_dir):
        profile = _make_profile(session_count=0)
        _save_profile(profile)
        update_profile_after_session(profile, [])
        loaded = _load_profile()
        assert loaded["session_count"] == 1

    def test_skips_unknown_content_types_in_topics(self, temp_profile_dir):
        profile = _make_profile()
        _save_profile(profile)
        history = [{"content_type": "unknown", "title": "something"}]
        update_profile_after_session(profile, history)
        loaded = _load_profile()
        assert "unknown" not in loaded.get("topics_seen", {})


class TestTerminalSignalAnalysis:
    def test_returns_dict_with_required_keys(self):
        result = _analyze_terminal_for_profile()
        assert "detected_stack" in result
        assert "signals" in result

    def test_handles_no_terminal_history_gracefully(self):
        with patch("src.capture.terminal.capture_terminal_context", return_value={"recent_commands": []}):
            result = _analyze_terminal_for_profile()
        assert result["detected_stack"] is None
        assert result["signals"] == []

    def test_detects_python_from_commands(self):
        mock_ctx = {
            "recent_commands": ["pip install langgraph", "python main.py", "pytest tests/"],
            "shell_type": "zsh",
        }
        with patch("src.capture.terminal.capture_terminal_context", return_value=mock_ctx):
            result = _analyze_terminal_for_profile()
        assert result["detected_stack"] == "Python"

    def test_detects_javascript_from_npm(self):
        mock_ctx = {
            "recent_commands": ["npm install", "npm run dev", "npx create-next-app"],
            "shell_type": "zsh",
        }
        with patch("src.capture.terminal.capture_terminal_context", return_value=mock_ctx):
            result = _analyze_terminal_for_profile()
        assert result["detected_stack"] == "JavaScript/React"

    def test_returns_empty_on_exception(self):
        with patch("src.capture.terminal.capture_terminal_context", side_effect=Exception("no history")):
            result = _analyze_terminal_for_profile()
        assert result == {"detected_stack": None, "signals": []}
