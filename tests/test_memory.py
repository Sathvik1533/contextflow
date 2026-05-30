"""Tests for TASK-013: Memory Agent (ChromaDB).

Tests cover:
- retrieve_memory returns empty structure on first session (no history)
- store_capture saves without crashing
- retrieve_memory finds related captures after storing
- format_memory_for_guide produces correct string
- pipeline never crashes when ChromaDB unavailable (graceful fallback)
"""

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_CONTEXT = {
    "content_type": "code",
    "title": "LangGraph StateGraph tutorial",
    "primary_text": "from langgraph.graph import StateGraph\ngraph = StateGraph(MyState)",
    "code_blocks": ["graph = StateGraph(MyState)", "app = graph.compile()"],
    "error_messages": [],
    "url_visible": "https://langchain-ai.github.io/langgraph/",
    "confidence": 0.92,
}

SAMPLE_GUIDANCE = {
    "summary": "User is learning LangGraph StateGraph construction.",
    "learning_path": ["Understand nodes", "Add edges", "Compile and invoke"],
    "questions_to_ask": ["What is the difference between add_edge and add_conditional_edges?"],
    "context_package": "=== ContextFlow Snapshot ===\n...",
}

ERROR_CONTEXT = {
    "content_type": "error",
    "title": "Python traceback",
    "primary_text": "TypeError: 'NoneType' object is not subscriptable",
    "code_blocks": [],
    "error_messages": ["TypeError: 'NoneType' object is not subscriptable"],
    "url_visible": None,
    "confidence": 0.88,
}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestRetrieveMemory:
    def test_empty_on_no_history(self, tmp_path, monkeypatch):
        """First session returns empty memory_context — never crashes."""
        monkeypatch.setattr(
            "src.agents.memory.CHROMA_DIR", tmp_path / "chroma"
        )
        from src.agents.memory import retrieve_memory
        result = retrieve_memory(SAMPLE_CONTEXT)

        assert isinstance(result, dict)
        assert result["past_captures"] == []
        assert result["topic_count"] == 0
        assert result["recurring_errors"] == []
        assert isinstance(result["depth_signal"], str)

    def test_returns_results_after_store(self, tmp_path, monkeypatch):
        """After storing a capture, retrieve finds related content."""
        monkeypatch.setattr(
            "src.agents.memory.CHROMA_DIR", tmp_path / "chroma"
        )
        from src.agents.memory import retrieve_memory, store_capture

        store_capture(SAMPLE_CONTEXT, SAMPLE_GUIDANCE)

        similar_context = {
            "content_type": "code",
            "title": "LangGraph nodes tutorial",
            "primary_text": "StateGraph nodes and edges in LangGraph",
            "code_blocks": [],
            "error_messages": [],
            "url_visible": None,
            "confidence": 0.85,
        }
        result = retrieve_memory(similar_context)

        assert isinstance(result["past_captures"], list)
        # At least one capture should be found (we just stored one)
        assert len(result["past_captures"]) >= 1

    def test_graceful_fallback_no_chromadb(self, monkeypatch):
        """If chromadb is not importable, returns empty structure — never crashes."""
        import builtins
        real_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "chromadb":
                raise ImportError("chromadb not installed")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", mock_import)

        # Reimport to pick up the mocked import
        import importlib
        import src.agents.memory as mem_mod
        importlib.reload(mem_mod)

        result = mem_mod.retrieve_memory(SAMPLE_CONTEXT)
        assert result["past_captures"] == []
        assert result["topic_count"] == 0


class TestStoreCapture:
    def test_store_returns_true_on_success(self, tmp_path, monkeypatch):
        """store_capture returns True when ChromaDB write succeeds."""
        monkeypatch.setattr(
            "src.agents.memory.CHROMA_DIR", tmp_path / "chroma"
        )
        from src.agents.memory import store_capture
        result = store_capture(SAMPLE_CONTEXT, SAMPLE_GUIDANCE)
        assert result is True

    def test_store_multiple_captures(self, tmp_path, monkeypatch):
        """Can store multiple captures without error."""
        monkeypatch.setattr(
            "src.agents.memory.CHROMA_DIR", tmp_path / "chroma"
        )
        from src.agents.memory import store_capture
        for _ in range(5):
            result = store_capture(SAMPLE_CONTEXT, SAMPLE_GUIDANCE)
            assert result is True

    def test_store_error_context(self, tmp_path, monkeypatch):
        """Stores error-type captures correctly."""
        monkeypatch.setattr(
            "src.agents.memory.CHROMA_DIR", tmp_path / "chroma"
        )
        from src.agents.memory import store_capture
        result = store_capture(ERROR_CONTEXT, SAMPLE_GUIDANCE)
        assert result is True


class TestFormatMemoryForGuide:
    def test_empty_returns_empty_string(self):
        """Empty memory_context produces empty string — no injection."""
        from src.agents.memory import format_memory_for_guide
        assert format_memory_for_guide({}) == ""
        assert format_memory_for_guide({"past_captures": [], "depth_signal": ""}) == ""

    def test_depth_signal_included(self):
        """Depth signal appears in formatted output."""
        from src.agents.memory import format_memory_for_guide
        memory = {
            "past_captures": [],
            "topic_count": 3,
            "recurring_errors": [],
            "depth_signal": "Seen 3 times — skip basics, focus on patterns.",
        }
        result = format_memory_for_guide(memory)
        assert "skip basics" in result
        assert "MEMORY DEPTH SIGNAL" in result

    def test_past_captures_included(self):
        """Past captures appear in formatted output with title and summary."""
        from src.agents.memory import format_memory_for_guide
        memory = {
            "past_captures": [
                {
                    "title": "LangGraph tutorial",
                    "summary": "User learned about StateGraph nodes.",
                    "timestamp": "2026-05-28T10:00:00",
                    "similarity": 0.87,
                    "content_type": "code",
                }
            ],
            "topic_count": 1,
            "recurring_errors": [],
            "depth_signal": "First time on this topic.",
        }
        result = format_memory_for_guide(memory)
        assert "LangGraph tutorial" in result
        assert "StateGraph nodes" in result

    def test_recurring_errors_included(self):
        """Recurring errors appear when detected."""
        from src.agents.memory import format_memory_for_guide
        memory = {
            "past_captures": [],
            "topic_count": 0,
            "recurring_errors": [
                {"error": "TypeError: NoneType", "when": "2026-05-27T14:00:00"}
            ],
            "depth_signal": "",
        }
        result = format_memory_for_guide(memory)
        assert "TypeError" in result
        assert "RECURRING ERROR" in result


class TestDepthSignal:
    def test_first_session_signal(self, tmp_path, monkeypatch):
        """First session produces 'start with fundamentals' signal."""
        monkeypatch.setattr(
            "src.agents.memory.CHROMA_DIR", tmp_path / "chroma"
        )
        from src.agents.memory import retrieve_memory
        result = retrieve_memory(SAMPLE_CONTEXT)
        assert "First time" in result["depth_signal"] or result["depth_signal"] == ""
