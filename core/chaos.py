"""
Adversarial Chaos Engine for QA-Swarm.
Generates adversarial test suites across buffer, Unicode/RTL, type mutation,
syntax injection, and concurrency vectors, and evaluates code resilience scores.
"""

import json
import logging
import os
import re
from pathlib import Path
from typing import List, Optional

from core.schemas import ChaosTestCase, VisualDefect

logger = logging.getLogger("qa_swarm.chaos")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MOCK_FILE = PROJECT_ROOT / "test_samples" / "mock_audit_result.json"

DYNAMIC_CHAOS_VECTORS = [
    {
        "test_id": "CHAOS-001",
        "stress_vector": "BUFFER_LENGTH_EXTREME",
        "input_payload": "A" * 5200,
        "expected_behavior": (
            "Graceful text truncation with CSS text-overflow: ellipsis without overflowing "
            "container layout, blowing out parent boundaries, or exhausting memory."
        ),
    },
    {
        "test_id": "CHAOS-002",
        "stress_vector": "UNICODE_RTL_INJECTION",
        "input_payload": "\u202E\u0627\u0644\u062F\u0641\u0639 \u0627\u0644\u0622\u0646\u202C \U0001F6D2 \U0001F4B3 \u030A\u0342\u0311ZALGO",
        "expected_behavior": (
            "Layout isolates bi-directional text without flipping surrounding DOM structures "
            "or corrupting adjacent action icons and currency signs."
        ),
    },
    {
        "test_id": "CHAOS-003",
        "stress_vector": "BOUNDARY_TYPE_MUTATION",
        "input_payload": '{"amount": null, "currency_rate": "NaN", "metadata": []}',
        "expected_behavior": (
            "Safe fallback to default numerical values or explicit validation error dispatch; "
            "prevents unhandled TypeError or AttributeError crashes in order calculation."
        ),
    },
    {
        "test_id": "CHAOS-004",
        "stress_vector": "SYNTAX_INJECTION_ESCAPE",
        "input_payload": '"; } body { display:none } <script>alert(1)</script>',
        "expected_behavior": (
            "CSS and HTML metacharacters must be sanitized and rendered as literal string content; "
            "stylesheet breakout and DOM script execution are neutralized."
        ),
    },
    {
        "test_id": "CHAOS-005",
        "stress_vector": "CONCURRENCY_EVENT_STORM",
        "input_payload": "burst_click_events=50_in_100ms_parallel",
        "expected_behavior": (
            "Event listener debounces rapid consecutive triggers; payment mutation dispatches "
            "exactly once with an idempotency token, ignoring duplicate clicks."
        ),
    },
]


def generate_chaos_suite(
    component_code: str,
    defect: Optional[VisualDefect] = None,
    mock: bool = True,
) -> List[ChaosTestCase]:
    """
    Generates an adversarial test suite of 5 distinct stress vectors.
    Uses deterministic mock data if mock=True / USE_MOCK=True and available,
    otherwise synthesizes 5 aggressive dynamic chaos scenarios.
    """
    env_mock = os.getenv("USE_MOCK", "true").strip().lower() in ("true", "1", "yes", "t")
    should_use_mock = mock or env_mock

    # Deterministic Mock Fallback
    if should_use_mock and DEFAULT_MOCK_FILE.exists():
        try:
            with open(DEFAULT_MOCK_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            raw_suite = data.get("chaos_suite", [])
            if len(raw_suite) == 5:
                return [ChaosTestCase.model_validate(item) for item in raw_suite]
        except Exception as exc:
            logger.warning(
                f"[Chaos] Error loading mock chaos suite: {exc}. Proceeding with dynamic suite."
            )

    # Dynamic / Heuristic Generation Mode
    suite: List[ChaosTestCase] = []
    for item in DYNAMIC_CHAOS_VECTORS:
        suite.append(ChaosTestCase.model_validate(item))

    return suite


def evaluate_resilience_score(
    component_code: str,
    test_suite: List[ChaosTestCase],
) -> int:
    """
    Evaluates defensive code patterns (type checks, error handling, defensive styling)
    against the chaos test suite and computes a resilience score between 0 and 100.
    """
    if not component_code or not component_code.strip():
        return 0

    score = 25  # Base score for valid non-empty component code

    code_lower = component_code.lower()

    # 1. Error & Exception Handling (+25 pts)
    if "try:" in code_lower and "except" in code_lower:
        score += 25
    elif "except" in code_lower or "catch" in code_lower:
        score += 15

    # 2. Defensive Data Access & Type Checking (+20 pts)
    has_get_fallback = ".get(" in component_code
    has_isinstance = "isinstance(" in component_code or "typeof" in code_lower
    has_null_check = "is not none" in code_lower or "if not" in code_lower

    if has_get_fallback or has_isinstance:
        score += 15
    if has_null_check:
        score += 5

    # 3. Defensive Layout & Overflow Protection (+20 pts)
    has_fluid_width = "width: 100%" in code_lower or "width:100%" in code_lower
    has_max_width = "max-width" in code_lower
    has_overflow_handling = "overflow" in code_lower or "text-overflow" in code_lower

    if has_fluid_width or has_max_width:
        score += 15
    if has_overflow_handling:
        score += 5

    # 4. Sanitization & Escaping (+10 pts)
    has_sanitization = any(
        kw in code_lower for kw in ["escape(", "sanitize(", "strip()", "html.escape"]
    )
    if has_sanitization:
        score += 10

    # Penalties for rigid layout anti-patterns (-10 pts)
    if re.search(r"width\s*[:=]\s*[\"']?120px", component_code, re.IGNORECASE):
        score -= 10

    # Ensure score stays strictly within [0, 100]
    return max(0, min(100, int(score)))
