"""
API Client and Mock Runner for QA-Swarm.
Loads environment variables, handles exponential backoff for network requests,
and provides deterministic fallback to local mock audit results when USE_MOCK is set
or when API keys are absent.
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Callable, Dict, Optional, TypeVar

from dotenv import load_dotenv
import requests

from core.schemas import QAAuditReport

logger = logging.getLogger("qa_swarm.client")
logging.basicConfig(level=logging.INFO)

T = TypeVar("T")


def with_exponential_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    retryable_statuses: tuple = (429, 500, 502, 503, 504),
) -> Callable:
    """
    Decorator executing network calls with exponential backoff and jitter.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args: Any, **kwargs: Any) -> T:
            delay = initial_delay
            last_exception: Optional[Exception] = None

            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except requests.RequestException as exc:
                    last_exception = exc
                    status_code = getattr(getattr(exc, "response", None), "status_code", None)
                    is_retryable = status_code in retryable_statuses or isinstance(
                        exc, (requests.ConnectionError, requests.Timeout)
                    )

                    if not is_retryable or attempt == max_retries:
                        logger.error(
                            f"[QA-Swarm] Request failed on attempt {attempt}/{max_retries}: {exc}"
                        )
                        raise

                    logger.warning(
                        f"[QA-Swarm] Attempt {attempt} failed ({exc}). Retrying in {delay:.2f}s..."
                    )
                    time.sleep(delay)
                    delay *= backoff_factor

            if last_exception:
                raise last_exception
            raise RuntimeError("Unexpected failure in exponential backoff loop")

        return wrapper
    return decorator


class QASwarmClient:
    """
    Core orchestrator client for QA-Swarm audit runs.
    """

    def __init__(
        self,
        env_file: Optional[Path | str] = None,
        mock_file_path: Optional[Path | str] = None,
    ) -> None:
        if env_file:
            load_dotenv(dotenv_path=env_file)
        else:
            load_dotenv()

        self.meta_api_key: Optional[str] = os.getenv("META_API_KEY", "").strip() or None
        self.fireworks_api_key: Optional[str] = os.getenv("FIREWORKS_API_KEY", "").strip() or None
        raw_mock = os.getenv("USE_MOCK", "true").strip().lower()
        self.use_mock: bool = raw_mock in ("true", "1", "yes", "t")

        # Resolve path to test_samples/mock_audit_result.json
        if mock_file_path:
            self.mock_file_path = Path(mock_file_path).resolve()
        else:
            project_root = Path(__file__).resolve().parent.parent
            self.mock_file_path = project_root / "test_samples" / "mock_audit_result.json"

    def load_mock_audit_report(self) -> QAAuditReport:
        """
        Loads and validates deterministic mock audit report from disk without network calls.
        """
        if not self.mock_file_path.exists():
            raise FileNotFoundError(
                f"Mock audit sample not found at expected location: {self.mock_file_path}"
            )

        with open(self.mock_file_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        return QAAuditReport.model_validate(raw_data)

    @with_exponential_backoff(max_retries=3, initial_delay=1.0)
    def _execute_remote_call(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes remote HTTP POST to model/vision inference service with retry handling.
        """
        headers = {
            "Authorization": f"Bearer {self.meta_api_key}",
            "Content-Type": "application/json",
        }
        response = requests.post(endpoint, json=payload, headers=headers, timeout=30.0)
        response.raise_for_status()
        return response.json()

    def run_audit(
        self,
        target_url: Optional[str] = None,
        screenshot_path: Optional[str | Path] = None,
    ) -> QAAuditReport:
        """
        Runs an end-to-end visual QA audit. Falls back gracefully to mock if USE_MOCK is true
        or when META_API_KEY is not configured.
        """
        if self.use_mock or not self.meta_api_key:
            logger.info(
                f"[QA-Swarm] USE_MOCK={self.use_mock} or META_API_KEY missing. "
                f"Loading deterministic report from: {self.mock_file_path.name}"
            )
            return self.load_mock_audit_report()

        # Real inference execution (for production wiring)
        logger.info(f"[QA-Swarm] Executing live audit for target: {target_url or screenshot_path}")
        payload = {
            "target_url": target_url,
            "screenshot": str(screenshot_path) if screenshot_path else None,
        }
        # Placeholder endpoint for real integration
        raw_response = self._execute_remote_call("https://api.meta.ai/v1/vision/audit", payload)
        return QAAuditReport.model_validate(raw_response)
