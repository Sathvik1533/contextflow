"""Tests for Guide agent."""

from unittest.mock import MagicMock, patch

import pytest

from src.agents.guide import run_guide, _parse_guide_response, _build_context_package


class TestGuide:
    """Test suite for Guide agent."""
    
    def test_valid_guide_response(self):
        """Guide should parse valid response correctly."""
        mock_response = MagicMock()
        mock_response.content = """SUMMARY: You're watching a React hooks tutorial. The video explains useState.

LEARNING PATH:
1. Pause at 3:45 where useState is explained
2. Open React documentation on hooks
3. Try creating a simple counter with useState

QUESTIONS TO ASK:
1. When should I use useState vs useReducer?
2. How do I optimize re-renders with hooks?"""
        
        extracted_context = {
            "content_type": "youtube",
            "title": "React Hooks Tutorial",
            "primary_text": "Learning about useState",
            "code_blocks": [],
            "error_messages": [],
            "url_visible": "https://youtube.com/watch?v=abc",
            "confidence": 0.9,
        }
        
        with patch.dict("os.environ", {"GROQ_API_KEY": "fake_key"}):
            with patch("src.agents.guide.ChatGroq") as mock_groq:
                mock_groq.return_value.invoke.return_value = mock_response
                
                result = run_guide(extracted_context, user_intent="learning React")
                
                assert "summary" in result
                assert "learning_path" in result
                assert "questions_to_ask" in result
                assert "context_package" in result
                assert len(result["learning_path"]) == 3
                assert len(result["questions_to_ask"]) == 2
    
    def test_parse_guide_response(self):
        """Should parse Guide's structured response."""
        raw_content = """SUMMARY: This is a test summary.

LEARNING PATH:
1. First step
2. Second step
3. Third step

QUESTIONS TO ASK:
1. First question?
2. Second question?"""
        
        result = _parse_guide_response(raw_content)
        
        assert result["summary"] == "This is a test summary."
        assert len(result["learning_path"]) == 3
        assert result["learning_path"][0] == "First step"
        assert len(result["questions_to_ask"]) == 2
        assert result["questions_to_ask"][0] == "First question?"
    
    def test_build_context_package(self):
        """Should build properly formatted context package."""
        extracted_context = {
            "content_type": "code",
            "title": "test.py",
            "primary_text": "def hello(): pass",
            "code_blocks": ["def hello(): pass"],
            "error_messages": [],
            "url_visible": None,
            "confidence": 0.85,
        }
        
        guidance = {
            "summary": "Test summary",
            "learning_path": ["Step 1", "Step 2"],
            "questions_to_ask": ["Question 1?", "Question 2?"],
        }
        
        package = _build_context_package(extracted_context, guidance)
        
        assert "=== ContextFlow Snapshot" in package
        assert "CONTENT TYPE: code" in package
        assert "TITLE: test.py" in package
        assert "def hello(): pass" in package
        assert "Question 1?" in package
        assert "=== END SNAPSHOT ===" in package
    
    def test_content_type_fallback(self):
        """Should fallback to 'other' for invalid content_type."""
        mock_response = MagicMock()
        mock_response.content = """SUMMARY: Generic summary.

LEARNING PATH:
1. Step 1
2. Step 2
3. Step 3

QUESTIONS TO ASK:
1. Question 1?
2. Question 2?"""
        
        extracted_context = {
            "content_type": "invalid_type",  # Invalid
            "title": "Test",
            "primary_text": "Test content",
            "code_blocks": [],
            "error_messages": [],
            "url_visible": None,
            "confidence": 0.8,
        }
        
        with patch.dict("os.environ", {"GROQ_API_KEY": "fake_key"}):
            with patch("src.agents.guide.ChatGroq") as mock_groq:
                mock_groq.return_value.invoke.return_value = mock_response
                
                result = run_guide(extracted_context)
                
                # Should not crash, should use 'other' prompt
                assert "summary" in result
    
    def test_missing_api_key(self):
        """Should raise ValueError if GROQ_API_KEY not set."""
        extracted_context = {
            "content_type": "code",
            "title": "test.py",
            "primary_text": "test",
            "code_blocks": [],
            "error_messages": [],
            "url_visible": None,
            "confidence": 0.8,
        }
        
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="GROQ_API_KEY not found"):
                run_guide(extracted_context)
