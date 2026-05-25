"""Tests for Observer agent."""

import json
from unittest.mock import MagicMock, patch

import pytest

from src.agents.observer import run_observer


# Full valid response matching new schema — reused across tests
VALID_RESPONSE = {
    "content_type": "youtube",
    "title": "LangGraph Tutorial",
    "primary_text": "This video explains state management in LangGraph",
    "headings": ["Introduction", "State Management"],
    "lists": ["Step 1: Define state", "Step 2: Add nodes"],
    "code_blocks": ["def my_func(): pass"],
    "error_messages": [],
    "url_visible": "https://youtube.com/watch?v=abc123",
    "tables": [],
    "confidence": 0.92,
}


class TestObserver:
    """Test suite for Observer agent."""

    def test_valid_json_response(self):
        """Observer should parse valid JSON response correctly."""
        mock_response = MagicMock()
        mock_response.content = json.dumps(VALID_RESPONSE)

        with patch.dict("os.environ", {"GROQ_API_KEY": "fake_key"}):
            with patch("src.agents.observer.ChatGroq") as mock_groq:
                mock_groq.return_value.invoke.return_value = mock_response

                result = run_observer("fake_base64_string")

                assert result["content_type"] == "youtube"
                assert result["title"] == "LangGraph Tutorial"
                assert result["confidence"] == 0.92
                assert len(result["code_blocks"]) == 1
                assert result["headings"] == ["Introduction", "State Management"]
                assert result["lists"] == ["Step 1: Define state", "Step 2: Add nodes"]
                assert result["tables"] == []

    def test_valid_json_with_user_intent(self):
        """Observer should work correctly when user_intent is provided."""
        mock_response = MagicMock()
        mock_response.content = json.dumps(VALID_RESPONSE)

        with patch.dict("os.environ", {"GROQ_API_KEY": "fake_key"}):
            with patch("src.agents.observer.ChatGroq") as mock_groq:
                mock_groq.return_value.invoke.return_value = mock_response

                result = run_observer("fake_base64_string", user_intent="learning LangGraph")

                assert result["content_type"] == "youtube"
                assert result["confidence"] == 0.92

    def test_strips_markdown_fences(self):
        """Observer should strip ```json fences from API response."""
        mock_response = MagicMock()
        mock_response.content = f"```json\n{json.dumps(VALID_RESPONSE)}\n```"

        with patch.dict("os.environ", {"GROQ_API_KEY": "fake_key"}):
            with patch("src.agents.observer.ChatGroq") as mock_groq:
                mock_groq.return_value.invoke.return_value = mock_response

                result = run_observer("fake_base64_string")

                assert result["content_type"] == "youtube"
                assert result["confidence"] == 0.92

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
            # Missing all other required fields
        })

        with patch.dict("os.environ", {"GROQ_API_KEY": "fake_key"}):
            with patch("src.agents.observer.ChatGroq") as mock_groq:
                mock_groq.return_value.invoke.return_value = mock_response

                with pytest.raises(ValueError, match="missing required fields"):
                    run_observer("fake_base64_string")

    def test_invalid_content_type(self):
        """Observer should raise ValueError if content_type is invalid."""
        bad_response = {**VALID_RESPONSE, "content_type": "invalid_type"}
        mock_response = MagicMock()
        mock_response.content = json.dumps(bad_response)

        with patch.dict("os.environ", {"GROQ_API_KEY": "fake_key"}):
            with patch("src.agents.observer.ChatGroq") as mock_groq:
                mock_groq.return_value.invoke.return_value = mock_response

                with pytest.raises(ValueError, match="Invalid content_type"):
                    run_observer("fake_base64_string")

    def test_invalid_confidence_value(self):
        """Observer should raise ValueError if confidence is not 0-1."""
        bad_response = {**VALID_RESPONSE, "confidence": 1.5}
        mock_response = MagicMock()
        mock_response.content = json.dumps(bad_response)

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
