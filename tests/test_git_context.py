"""Tests for TASK-016: Git Context Capture (src/capture/git.py).

Tests cover:
- capture_git_context returns valid dict in a real git repo (this project IS a git repo)
- capture_git_context returns is_git_repo=False for a non-git directory
- format_git_for_guide produces correct string from git context
- format_git_for_guide returns empty string when is_git_repo=False
- _run_git handles command failure gracefully
"""

import os
import tempfile

import pytest

from src.capture.git import capture_git_context, format_git_for_guide


class TestCaptureGitContext:
    def test_detects_real_git_repo(self):
        """Running inside ContextFlow project — must detect git repo."""
        # We are currently inside a git repo (ContextFlow itself)
        result = capture_git_context()

        assert result["is_git_repo"] is True
        assert isinstance(result["branch"], str)
        assert len(result["branch"]) > 0
        assert isinstance(result["last_commits"], list)
        assert isinstance(result["uncommitted_files"], list)
        assert isinstance(result["repo_root"], str)

    def test_returns_false_for_non_git_directory(self, tmp_path):
        """A temp directory with no git repo returns is_git_repo=False."""
        result = capture_git_context(cwd=str(tmp_path))

        assert result["is_git_repo"] is False
        assert result["branch"] == ""
        assert result["last_commits"] == []
        assert result["uncommitted_files"] == []

    def test_last_commits_are_strings(self):
        """Each commit in last_commits is a non-empty string."""
        result = capture_git_context()

        if result["is_git_repo"] and result["last_commits"]:
            for commit in result["last_commits"]:
                assert isinstance(commit, str)
                assert len(commit) > 0

    def test_max_three_commits_returned(self):
        """Never returns more than 3 commits."""
        result = capture_git_context()

        assert len(result["last_commits"]) <= 3

    def test_max_ten_uncommitted_files(self):
        """Never returns more than 10 uncommitted files."""
        result = capture_git_context()

        assert len(result["uncommitted_files"]) <= 10

    def test_graceful_fallback_on_invalid_cwd(self):
        """Non-existent directory returns empty structure, never crashes."""
        result = capture_git_context(cwd="/this/path/does/not/exist/anywhere")

        assert isinstance(result, dict)
        assert result["is_git_repo"] is False


class TestFormatGitForGuide:
    def test_empty_when_not_git_repo(self):
        """Returns empty string when is_git_repo is False."""
        result = format_git_for_guide({"is_git_repo": False})
        assert result == ""

    def test_empty_when_empty_dict(self):
        """Returns empty string for empty dict input."""
        result = format_git_for_guide({})
        assert result == ""

    def test_branch_included_in_output(self):
        """Branch name appears in formatted output."""
        git_context = {
            "is_git_repo": True,
            "branch": "feature/memory-agent",
            "last_commits": [],
            "uncommitted_files": [],
            "repo_root": "/Users/test/project",
        }
        result = format_git_for_guide(git_context)

        assert "feature/memory-agent" in result
        assert "GIT CONTEXT" in result

    def test_commits_included_in_output(self):
        """Last commits appear in formatted output."""
        git_context = {
            "is_git_repo": True,
            "branch": "main",
            "last_commits": [
                "abc1234 feat: add memory agent",
                "def5678 fix: silent exception in store_capture",
            ],
            "uncommitted_files": [],
            "repo_root": "/Users/test/project",
        }
        result = format_git_for_guide(git_context)

        assert "feat: add memory agent" in result
        assert "fix: silent exception" in result

    def test_uncommitted_files_included(self):
        """Uncommitted files appear in formatted output."""
        git_context = {
            "is_git_repo": True,
            "branch": "main",
            "last_commits": [],
            "uncommitted_files": ["M src/agents/memory.py", "M src/graph/nodes.py"],
            "repo_root": "/Users/test/project",
        }
        result = format_git_for_guide(git_context)

        assert "memory.py" in result

    def test_real_repo_produces_valid_output(self):
        """End-to-end: capture + format produces non-empty string in real repo."""
        git_context = capture_git_context()

        if git_context["is_git_repo"]:
            formatted = format_git_for_guide(git_context)
            assert len(formatted) > 0
            assert "GIT CONTEXT" in formatted
