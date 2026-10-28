"""
Playwright Live Browser Capture Module for QA-Swarm.
Provides automated headless screenshot capture of live web applications
with standard 1280x800 desktop viewport, graceful cloud fallback for Hugging Face Spaces,
and resilient timeout/error handling.
"""

import logging
from pathlib import Path
import shutil

from playwright.sync_api import Error as PlaywrightError, TimeoutError as PlaywrightTimeoutError, sync_playwright

logger = logging.getLogger("qa_swarm.browser")
logging.basicConfig(level=logging.INFO)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SAMPLE_UI = PROJECT_ROOT / "test_samples" / "sample_ui.png"


def capture_url_screenshot(
    url: str,
    output_path: str = "test_samples/live_capture.png",
    timeout_ms: int = 15000,
    fallback_on_error: bool = True,
) -> str:
    """Captures standard 1280x800 desktop screenshot using Playwright Chromium with low memory footprint."""
    if not url or not url.strip():
        raise ValueError("Target URL cannot be empty.")

    target_path = Path(output_path).resolve()
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # Normalize url scheme if missing (e.g. localhost:3000 -> http://localhost:3000)
    trimmed_url = url.strip()
    if not trimmed_url.startswith(("http://", "https://", "file://", "data:")):
        if trimmed_url.startswith("localhost") or trimmed_url.startswith("127.0.0.1"):
            trimmed_url = f"http://{trimmed_url}"
        else:
            trimmed_url = f"https://{trimmed_url}"

    logger.info(f"[QA-Swarm:Browser] Capturing live screenshot of: {trimmed_url} -> {target_path}")

    browser = None
    context = None
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"],
            )
            try:
                # Desktop viewport standard 1280x800
                context = browser.new_context(
                    viewport={"width": 1280, "height": 800},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) QA-Swarm/1.0",
                )
                page = context.new_page()

                # Navigate with timeout and wait until domcontentloaded
                page.goto(
                    trimmed_url,
                    timeout=timeout_ms,
                    wait_until="domcontentloaded",
                )

                # Capture standard desktop viewport screenshot
                page.screenshot(path=str(target_path), full_page=False)
                logger.info(f"[QA-Swarm:Browser] Successfully saved live screenshot to: {target_path}")
                return str(target_path)
            finally:
                if context is not None:
                    try:
                        context.close()
                    except Exception as close_err:
                        logger.debug(f"[QA-Swarm:Browser] Context close error: {close_err}")
                if browser is not None:
                    try:
                        browser.close()
                    except Exception as close_err:
                        logger.debug(f"[QA-Swarm:Browser] Browser close error: {close_err}")

    except (PlaywrightTimeoutError, PlaywrightError, Exception) as exc:
        logger.warning(
            f"[QA-Swarm:Browser] Playwright capture failed or browser unavailable for '{trimmed_url}' ({exc}). "
            f"Applying resilient fallback to 'test_samples/sample_ui.png'."
        )
        if fallback_on_error:
            if DEFAULT_SAMPLE_UI.exists():
                try:
                    shutil.copyfile(str(DEFAULT_SAMPLE_UI), str(target_path))
                    return str(target_path)
                except Exception:
                    return str(DEFAULT_SAMPLE_UI)
            return "test_samples/sample_ui.png"

        raise RuntimeError(f"Playwright navigation failed on '{trimmed_url}': {exc}") from exc
