"""Tests for screen capture functionality."""

import base64
import os

import pytest
from PIL import Image

from src.capture.screen import capture_screen, save_screenshot_from_b64


def test_capture_screen_returns_valid_base64():
    """Test that capture_screen returns a valid base64 string."""
    result = capture_screen()
    
    assert "screenshot_b64" in result
    assert "capture_timestamp" in result
    assert "original_size" in result
    
    # Base64 should be non-empty string
    assert isinstance(result["screenshot_b64"], str)
    assert len(result["screenshot_b64"]) > 0
    
    # Should be valid base64 (doesn't raise)
    base64.b64decode(result["screenshot_b64"])


def test_capture_screen_produces_valid_png():
    """Test that the base64 decodes to a valid PNG image."""
    result = capture_screen()
    
    # Decode and verify it's a valid image
    img_bytes = base64.b64decode(result["screenshot_b64"])
    img = Image.open(io.BytesIO(img_bytes))
    
    assert img.format == "PNG"
    assert img.size == (1280, 800)  # Default resize


def test_capture_screen_custom_resize():
    """Test that custom resize dimensions work."""
    result = capture_screen(resize_to=(640, 400))
    
    img_bytes = base64.b64decode(result["screenshot_b64"])
    img = Image.open(io.BytesIO(img_bytes))
    
    assert img.size == (640, 400)


def test_capture_screen_invalid_monitor():
    """Test that invalid monitor index raises IndexError."""
    with pytest.raises(IndexError, match="Monitor .* not found"):
        capture_screen(monitor_index=99)


def test_save_screenshot_from_b64(tmp_path):
    """Test saving a screenshot to disk."""
    result = capture_screen()
    filepath = tmp_path / "test_screenshot.png"
    
    save_screenshot_from_b64(result["screenshot_b64"], str(filepath))
    
    assert filepath.exists()
    
    # Verify it's a valid PNG
    img = Image.open(filepath)
    assert img.format == "PNG"


# Import io for test_capture_screen_produces_valid_png
import io
