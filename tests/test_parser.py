"""Tests for Content Parser (src/utils/parser.py).

The parser is pure Python — no API calls, no mocks needed.
Three cases: happy path, unknown content type, broken input.
"""

import pytest

from src.utils.parser import parse_context


# --- Shared test fixture: a full Observer output with all 10 fields ---
# This simulates exactly what observer_node writes into state
FULL_CONTEXT = {
    "content_type": "code",
    "title": "graph/builder.py — LangGraph wiring",
    "primary_text": "def build_graph(): ...",
    "headings": ["Builder", "Nodes", "Edges"],
    "lists": ["capture_node", "observer_node"],
    "code_blocks": ["graph = StateGraph(ContextFlowState)", "graph.compile()"],
    "error_messages": [],
    "url_visible": None,
    "tables": [],
    "confidence": 0.91,
}


class TestParser:

    def test_happy_path_filters_to_correct_fields(self):
        """For content_type='code', parser keeps only code-relevant fields.

        WHY this test exists:
        Guide receives filtered context. If parser breaks and returns all 10 fields,
        Guide gets noise (tables, lists, headings) that don't help for code advice.
        This test enforces the filter contract.
        """
        result = parse_context(FULL_CONTEXT)

        # These fields matter for code content
        assert "content_type" in result
        assert "title" in result
        assert "code_blocks" in result
        assert "error_messages" in result
        assert "confidence" in result

        # These fields are noise for code — parser should have dropped them
        assert "headings" not in result
        assert "lists" not in result
        assert "tables" not in result
        assert "primary_text" not in result

    def test_unknown_content_type_returns_everything(self):
        """For an unknown content_type, parser should return full context unchanged.

        WHY this test exists:
        Observer might return an unexpected content_type in the wild.
        Parser must not crash or silently drop data — it falls back to 'other'
        which means keep everything. Guide can still work with full context.
        """
        unknown_context = {**FULL_CONTEXT, "content_type": "webpage"}  # not in our list

        result = parse_context(unknown_context)

        # All original fields must be present — no data dropped
        for key in FULL_CONTEXT:
            assert key in result, f"Expected field '{key}' to be present for unknown type"

    def test_empty_input_raises_value_error(self):
        """Empty dict should raise ValueError, not silently return empty result.

        WHY this test exists:
        guide_node calls parse_context() before calling run_guide().
        If parse_context() silently returns {} when given bad input,
        run_guide() crashes with a confusing KeyError deep in the stack.
        We want the error raised here, with a clear message, not later.
        """
        with pytest.raises(ValueError, match="empty"):
            parse_context({})

    def test_missing_content_type_raises_value_error(self):
        """Dict without content_type field should raise ValueError.

        WHY this test exists:
        Parser uses content_type to decide which fields to keep.
        Without it, every decision downstream is wrong.
        Catch it at the boundary, not silently.
        """
        no_type_context = {
            "title": "something",
            "primary_text": "some text",
            "confidence": 0.8,
            # content_type deliberately missing
        }

        with pytest.raises(ValueError, match="content_type"):
            parse_context(no_type_context)

    def test_other_content_type_returns_everything(self):
        """For content_type='other', parser keeps all fields (None = no filter).

        WHY this test exists:
        'other' is the explicit passthrough type — desktop, settings, forms.
        Guide needs everything to make sense of an unclassified screen.
        This ensures the None branch in FIELDS_BY_TYPE works correctly.
        """
        other_context = {**FULL_CONTEXT, "content_type": "other"}

        result = parse_context(other_context)

        for key in FULL_CONTEXT:
            assert key in result
