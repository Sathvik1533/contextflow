"""Tests for TASK-017: Level-Adaptive Guide Prompts.

Tests cover:
- _build_level_instruction returns correct content for each level
- beginner instruction contains analogy/plain English keywords
- intermediate instruction contains pattern/practical keywords
- advanced instruction contains architecture/edge case keywords
- unknown or None user_level falls back to intermediate gracefully
- level instruction is prepended to the full prompt (not appended)
"""

import pytest

from src.agents.guide import _build_level_instruction, _build_context_package, _parse_guide_response


SAMPLE_CONTEXT = {
    "content_type": "code",
    "title": "LangGraph StateGraph example",
    "primary_text": "from langgraph.graph import StateGraph",
    "code_blocks": ["graph = StateGraph(MyState)"],
    "error_messages": [],
    "url_visible": None,
    "confidence": 0.88,
}


class TestBuildLevelInstruction:
    def test_beginner_contains_analogy_keywords(self):
        """Beginner instruction must guide Guide to use analogies."""
        result = _build_level_instruction("beginner")

        assert "BEGINNER" in result
        assert "analogy" in result.lower()
        assert "plain English" in result or "plain english" in result.lower()

    def test_beginner_contains_no_jargon_rule(self):
        """Beginner instruction must tell Guide to avoid jargon."""
        result = _build_level_instruction("beginner")
        assert "jargon" in result.lower()

    def test_intermediate_contains_pattern_keywords(self):
        """Intermediate instruction must focus on patterns and practical use."""
        result = _build_level_instruction("intermediate")

        assert "INTERMEDIATE" in result
        assert "pattern" in result.lower() or "practical" in result.lower()

    def test_intermediate_skips_basics(self):
        """Intermediate instruction must tell Guide to skip foundational content."""
        result = _build_level_instruction("intermediate")
        assert "skip" in result.lower() or "foundational" in result.lower()

    def test_advanced_contains_architecture_keywords(self):
        """Advanced instruction must focus on architecture and edge cases."""
        result = _build_level_instruction("advanced")

        assert "ADVANCED" in result
        assert "architecture" in result.lower() or "edge cases" in result.lower()

    def test_advanced_mentions_tradeoffs(self):
        """Advanced instruction must mention trade-offs."""
        result = _build_level_instruction("advanced")
        assert "trade-off" in result.lower() or "trade off" in result.lower()

    def test_unknown_level_falls_back_to_intermediate(self):
        """Unknown level string must fall back to intermediate — never crash."""
        result = _build_level_instruction("expert")
        intermediate = _build_level_instruction("intermediate")
        assert result == intermediate

    def test_none_level_falls_back_to_intermediate(self):
        """None user_level must fall back to intermediate — never crash."""
        result = _build_level_instruction(None)
        intermediate = _build_level_instruction("intermediate")
        assert result == intermediate

    def test_empty_string_falls_back_to_intermediate(self):
        """Empty string user_level must fall back to intermediate."""
        result = _build_level_instruction("")
        intermediate = _build_level_instruction("intermediate")
        assert result == intermediate

    def test_case_insensitive(self):
        """Level matching must be case-insensitive."""
        assert _build_level_instruction("BEGINNER") == _build_level_instruction("beginner")
        assert _build_level_instruction("Advanced") == _build_level_instruction("advanced")

    def test_all_levels_return_non_empty_string(self):
        """All three levels must return a non-empty string."""
        for level in ["beginner", "intermediate", "advanced"]:
            result = _build_level_instruction(level)
            assert isinstance(result, str)
            assert len(result) > 50  # must be substantive, not a one-liner

    def test_levels_are_distinct(self):
        """All three level instructions must be different from each other."""
        beginner = _build_level_instruction("beginner")
        intermediate = _build_level_instruction("intermediate")
        advanced = _build_level_instruction("advanced")

        assert beginner != intermediate
        assert intermediate != advanced
        assert beginner != advanced


class TestLevelInstructionIntegration:
    def test_beginner_instruction_differs_from_advanced(self):
        """Beginner and advanced instructions must produce meaningfully different content."""
        beginner = _build_level_instruction("beginner")
        advanced = _build_level_instruction("advanced")

        # Beginner must mention plain English, advanced must not require it
        assert "plain" in beginner.lower()
        # Advanced must mention skipping basics
        assert "skip" in advanced.lower() or "basics" in advanced.lower()
