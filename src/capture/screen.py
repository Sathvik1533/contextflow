"""Screen capture utilities using mss.

This module handles the hardware interaction layer — grabbing pixels from
the monitor and converting them to base64-encoded PNG strings.
"""

import base64
import io
from datetime import datetime, timezone

import mss
from PIL import Image


def capture_screen(monitor_index: int = 1, resize_to: tuple[int, int] = (1280, 800)) -> dict:
    """Capture the specified monitor and return base64-encoded PNG.
    
    Args:
        monitor_index: Monitor to capture (1 = primary, 2 = secondary, etc.)
        resize_to: Target dimensions (width, height). Smaller = fewer tokens for Vision API.
    
    Returns:
        dict with keys:
            - screenshot_b64: Base64-encoded PNG string
            - capture_timestamp: ISO 8601 timestamp
            - original_size: Tuple of (width, height) before resize
    
    Raises:
        mss.exception.ScreenShotError: If screen recording permission denied (macOS)
        IndexError: If monitor_index doesn't exist
    """
    with mss.mss() as sct:
        # Validate monitor index
        if monitor_index >= len(sct.monitors):
            available = len(sct.monitors) - 1  # monitors[0] is "all monitors"
            raise IndexError(
                f"Monitor {monitor_index} not found. Available monitors: 1-{available}"
            )
        
        # Grab the monitor
        monitor = sct.monitors[monitor_index]
        screenshot = sct.grab(monitor)
        
        # Convert to PIL Image (mss returns BGRA, we need RGB)
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        original_size = img.size
        
        # Resize to reduce token cost (Vision API charges by image dimensions)
        if resize_to:
            img = img.resize(resize_to, Image.Resampling.LANCZOS)
        
        # Encode to base64 PNG
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        b64_string = base64.b64encode(buffer.getvalue()).decode("utf-8")
        
        return {
            "screenshot_b64": b64_string,
            "capture_timestamp": datetime.now(timezone.utc).isoformat(),
            "original_size": original_size,
        }


def save_screenshot_from_b64(b64_string: str, filepath: str) -> None:
    """Save a base64-encoded screenshot to disk (for debugging/testing).
    
    Args:
        b64_string: Base64-encoded PNG string
        filepath: Where to save (e.g., "test_screenshot.png")
    """
    img_bytes = base64.b64decode(b64_string)
    with open(filepath, "wb") as f:
        f.write(img_bytes)
