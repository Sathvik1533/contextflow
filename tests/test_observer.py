"""Tests for Observer agent (Gemini Vision integration)."""

import json
from unittest.mock import MagicMock, patch

import pytest

from src.agents.observer import _strip_markdown_fences, run_observer


def test_strip_markdown_fences_with_json_fence():
    """Test stripping ```json fences."""
    input_text = """```json
{
  "content_type": "youtube",
  "title": "Test"
}
```"""
    
    result = _strip_markdown_fences(input_text)
    
    # Should be valid JSON now
    parsed = json.loads(result)
    assert parsed["content_type"] == "youtube"


def test_strip_markdown_fences_with_plain_fence():
    """Test stripping ``` fences without language specifier."""
    input_text = """```
{"content_type": "code"}
```"""
    
    result = _strip_markdown_fences(input_text)
    parsed = json.loads(result)
    assert parsed["content_type"] == "code"


def test_strip_markdown_fences_no_fences():
    """Test that clean JSON passes through unchanged."""
    input_text = '{"content_type": "documentation"}'
    
    result = _strip_markdown_fences(input_text)
    
    assert result == input_text


def test_run_observer_valid_response():
    """Test run_observer with a valid Gemini response."""
    mock_response = MagicMock()
    mock_response.content = json.dumps({
        "content_type": "youtube",
        "title": "LangGraph Tutorial",
        "primary_text": "Learn how to build multi-agent systems",
        "code_blocks": [],
        "error_messages": [],
        "url_visible": "https://youtube.com/watch?v=abc",
        "confidence": 0.92,
    })
    
    with patch("src.agents.observer.ChatGoogleGenerativeAI") as mock_llm_class:
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_response
        mock_llm_class.return_value = mock_llm
        
        result = run_observer("fake_base64_string", api_key="test_key")
    
    assert result["content_type"] == "youtube"
    assert result["title"] == "LangGraph Tutorial"
    assert result["confidence"] == 0.92


def test_run_observer_with_markdown_fences():
    """Test that run_observer handles markdown fences correctly."""
    mock_response = MagicMock()
    mock_response.content = """```json
{
  "content_type": "code",
  "title": "main.py",
  "primary_text": "Python code visible",
  "code_blocks": ["def main(): pass"],
  "error_messages": [],
  "url_visible": null,
  "confidence": 0.88
}
```"""
    
    with patch("src.agents.observer.ChatGoogleGenerativeAI") as mock_llm_class:
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_response
        mock_llm_class.return_value = mock_llm
        
        result = run_observer("fake_base64", api_key="test_key")
    
    assert result["content_type"] == "code"
    assert result["confidence"] == 0.88


def test_run_observer_invalid_json():
    """Test that run_observer raises ValueError on invalid JSON."""
    mock_response = MagicMock()
    mock_response.content = "This is not JSON, just prose explanation"
    
    with patch("src.agents.observer.ChatGoogleGenerativeAI") as mock_llm_class:
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_response
        mock_llm_class.return_value = mock_llm
        
        with pytest.raises(ValueError, match="invalid JSON"):
            run_observer("fake_base64", api_key="test_key")


def test_run_observer_missing_required_fields():
    """Test that run_observer raises ValueError if required fields missing."""
    mock_response = MagicMock()
    mock_response.content = json.dumps({
        "content_type": "youtube",
        # Missing "title" and "confidence"
    })
    
    with patch("src.agents.observer.ChatGoogleGenerativeAI") as mock_llm_class:
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_response
        mock_llm_class.return_value = mock_llm
        
        with pytest.raises(ValueError, match="missing required fields"):
            run_observer("fake_base64", api_key="test_key")


def test_run_observer_confidence_not_number():
    """Test that run_observer raises ValueError if confidence is not a number."""
    mock_response = MagicMock()
    mock_response.content = json.dumps({
        "content_type": "youtube",
        "title": "Test",
        "confidence": "high",  # Should be a number
    })
    
    with patch("src.agents.observer.ChatGoogleGenerativeAI") as mock_llm_class:
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_response
        mock_llm_class.return_value = mock_llm
        
        with pytest.raises(ValueError, match="confidence must be a number"):
            run_observer("fake_base64", api_key="test_key")
