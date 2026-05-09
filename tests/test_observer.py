"""Tests for Observer agent."""

import json
from unittest.mock import MagicMock, patch

import pytest

from src.agents.observer import run_observer


class TestObserver:
    """Test suite for Observer agent."""
    
    def test_valid_json_response(self):
        """Observer should parse valid JSON response correctly."""
        mock_response = MagicMock()
        mock_response.content = json.dumps({
            "content_type": "youtube",
            "title": "LangGraph Tutorial",
            "primary_text": "This video explains state management",
            "code_blocks": ["def my_func(): pass"],
            "error_messages": [],
            "url_visible": "https://youtube.com/watch?v=abc123",
            "confidence": 0.92,
        })
        
        with patch.dict("os.environ", {"GROQ_API_KEY": "fake_key"}):
            with patch("src.agents.observer.ChatGroq") as mock_groq:
                mock_groq.return_value.invoke.return_value = mock_response
                
                result = run_observer("fake_base64_string")
                
                assert result["content_type"] == "youtube"
                assert result["title"] == "LangGraph Tutorial"
                assert result["confidence"] == 0.92
                assert len(result["code_blocks"]) == 1
    
    def test_strips_markdown_fences(self):
        """Observer should strip ```json fences from API response."""
        mock_response = MagicMock()
        # API sometimes returns markdown-wrapped JSON
        mock_response.content = """```json
{
  "content_type": "documentation",
  "title": "Python Docs",
  "primary_text": "Learn Python",
  "code_blocks": [],
  "error_messages": [],
  "url_visible": null,
  "confidence": 0.85
}
```"""
        
        with patch.dict("os.environ", {"GROQ_API_KEY": "fake_key"}):
            with patch("src.agents.observer.ChatGroq") as mock_groq:
                mock_groq.return_value.invoke.return_value = mock_response
                
                result = run_observer("fake_base64_string")
                
                assert result["content_type"] == "documentation"
                assert result["confidence"] == 0.85
    
    def test_invalid_json_raises_error(self):
        """Observer should raise ValueError if API returns invalid JSON."""
        mock_response = MagicMock()
        mock_response.content = "This is not JSON at all"
        
        with patch.dict("os.environ", {"GROQ_API_KEY": "fake_key"}):
            with patch("src.agents.observer.ChatGroq") as mock_groq:
                mock_groq.return_value.invoke.return_value = mock_response
                
                with pytest.raises(ValueError, match="invalid JSON"):
                    run_observer("fake_base64_string")
    
    def test_missing_required_fields(self):
        """Observer should raise ValueError if required fields are missing."""
        mock_response = MagicMock()
        mock_response.content = json.dumps({
            "content_type": "code",
            "title": "VS Code",
            # Missing: primary_text, code_blocks, error_messages, url_visible, confidence
        })
        
        with patch.dict("os.environ", {"GROQ_API_KEY": "fake_key"}):
            with patch("src.agents.observer.ChatGroq") as mock_groq:
                mock_groq.return_value.invoke.return_value = mock_response
                
                with pytest.raises(ValueError, match="missing required fields"):
                    run_observer("fake_base64_string")
    
    def test_invalid_content_type(self):
        """Observer should raise ValueError if content_type is invalid."""
        mock_response = MagicMock()
        mock_response.content = json.dumps({
            "content_type": "invalid_type",  # Not in allowed list
            "title": "Test",
            "primary_text": "Test",
            "code_blocks": [],
            "error_messages": [],
            "url_visible": None,
            "confidence": 0.8,
        })
        
        with patch.dict("os.environ", {"GROQ_API_KEY": "fake_key"}):
            with patch("src.agents.observer.ChatGroq") as mock_groq:
                mock_groq.return_value.invoke.return_value = mock_response
                
                with pytest.raises(ValueError, match="Invalid content_type"):
                    run_observer("fake_base64_string")
    
    def test_invalid_confidence_value(self):
        """Observer should raise ValueError if confidence is not 0-1."""
        mock_response = MagicMock()
        mock_response.content = json.dumps({
            "content_type": "code",
            "title": "Test",
            "primary_text": "Test",
            "code_blocks": [],
            "error_messages": [],
            "url_visible": None,
            "confidence": 1.5,  # Invalid: > 1.0
        })
        
        with patch.dict("os.environ", {"GROQ_API_KEY": "fake_key"}):
            with patch("src.agents.observer.ChatGroq") as mock_groq:
                mock_groq.return_value.invoke.return_value = mock_response
                
                with pytest.raises(ValueError, match="Invalid confidence"):
                    run_observer("fake_base64_string")
    
    def test_missing_api_key(self):
        """Observer should raise ValueError if GROQ_API_KEY not set."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="GROQ_API_KEY not found"):
                run_observer("fake_base64_string")
