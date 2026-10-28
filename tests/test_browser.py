"""
Unit tests for Playwright live browser capture (core/browser.py).
"""

from pathlib import Path
import pytest

from core.browser import capture_url_screenshot

TEST_SAMPLES_DIR = Path(__file__).resolve().parent.parent / "test_samples"


def test_capture_url_screenshot_empty_url_raises():
    """Validates that empty URL inputs raise ValueError."""
    with pytest.raises(ValueError, match="Target URL cannot be empty"):
        capture_url_screenshot("")


def test_capture_url_screenshot_with_data_url():
    """
    Validates that capture_url_screenshot successfully launches headless Chromium,
    navigates to a self-contained data URL, and writes a valid PNG file.
    """
    out_file = TEST_SAMPLES_DIR / "temp_browser_test.png"
    try:
        result = capture_url_screenshot(
            url="data:text/html,<html><body><h1 style='color:red;'>Live Test</h1></body></html>",
            output_path=str(out_file),
            timeout_ms=5000,
        )
        assert Path(result).exists()
        assert Path(result).stat().st_size > 0
    finally:
        if out_file.exists():
            out_file.unlink()


def test_capture_url_screenshot_fallback_on_unreachable_host():
    """
    Validates that unreachable hosts trigger a resilient fallback to sample_ui.png
    without raising exceptions or crashing.
    """
    out_file = TEST_SAMPLES_DIR / "fallback_capture.png"
    try:
        result = capture_url_screenshot(
            url="http://invalid.nonexistent.domain.test:9999",
            output_path=str(out_file),
            timeout_ms=2000,
            fallback_on_error=True,
        )
        assert Path(result).exists()
    finally:
        if out_file.exists():
            out_file.unlink()


def test_capture_url_screenshot_invalid_host_raises_when_fallback_disabled():
    """
    Validates that if fallback_on_error is False, RuntimeError is raised.
    """
    out_file = TEST_SAMPLES_DIR / "should_not_exist.png"
    try:
        with pytest.raises(RuntimeError):
            capture_url_screenshot(
                url="http://invalid.nonexistent.domain.test:9999",
                output_path=str(out_file),
                timeout_ms=2000,
                fallback_on_error=False,
            )
    finally:
        if out_file.exists():
            out_file.unlink()
