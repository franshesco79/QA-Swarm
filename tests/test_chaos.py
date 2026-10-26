"""
Unit tests for QA-Swarm core/chaos.py module.
Verifies adversarial chaos suite generation, Pydantic validation,
vector diversity, and resilience score boundaries.
"""

from pathlib import Path
import pytest

from core.schemas import ChaosTestCase, VisualDefect
from core.chaos import generate_chaos_suite, evaluate_resilience_score

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BROKEN_COMPONENT_PATH = PROJECT_ROOT / "test_samples" / "broken_component.py"


@pytest.fixture
def sample_component_code() -> str:
    assert BROKEN_COMPONENT_PATH.exists(), f"Missing: {BROKEN_COMPONENT_PATH}"
    with open(BROKEN_COMPONENT_PATH, "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def sample_defect() -> VisualDefect:
    return VisualDefect(
        element_name="btn_purchase",
        bbox=[420.0, 150.0, 480.0, 310.0],
        defect_type="LAYOUT_OVERFLOW",
        severity="CRITICAL",
    )


def test_generate_chaos_suite_returns_five_cases(sample_component_code, sample_defect):
    """
    Verifies that generate_chaos_suite returns exactly 5 test cases in both mock and dynamic modes.
    """
    suite_mock = generate_chaos_suite(sample_component_code, sample_defect, mock=True)
    assert isinstance(suite_mock, list)
    assert len(suite_mock) == 5

    suite_dyn = generate_chaos_suite(sample_component_code, sample_defect, mock=False)
    assert isinstance(suite_dyn, list)
    assert len(suite_dyn) == 5


def test_chaos_test_cases_pydantic_validation(sample_component_code, sample_defect):
    """
    Validates that each generated test case conforms strictly to ChaosTestCase Pydantic schema
    with valid, non-empty fields.
    """
    for mock_mode in [True, False]:
        suite = generate_chaos_suite(sample_component_code, sample_defect, mock=mock_mode)
        for case in suite:
            assert isinstance(case, ChaosTestCase)
            assert isinstance(case.test_id, str) and len(case.test_id.strip()) > 0
            assert isinstance(case.input_payload, str) and len(case.input_payload.strip()) > 0
            assert isinstance(case.stress_vector, str) and len(case.stress_vector.strip()) > 0
            assert isinstance(case.expected_behavior, str) and len(case.expected_behavior.strip()) > 0


def test_chaos_stress_vectors_are_diverse(sample_component_code, sample_defect):
    """
    Verifies that all 5 stress vectors in a suite are unique and cover diverse attack categories.
    """
    suite_mock = generate_chaos_suite(sample_component_code, sample_defect, mock=True)
    mock_vectors = {case.stress_vector for case in suite_mock}
    assert len(mock_vectors) == 5, f"Expected 5 unique vectors in mock suite, got: {mock_vectors}"

    suite_dyn = generate_chaos_suite(sample_component_code, sample_defect, mock=False)
    dyn_vectors = {case.stress_vector for case in suite_dyn}
    assert len(dyn_vectors) == 5, f"Expected 5 unique vectors in dynamic suite, got: {dyn_vectors}"


def test_evaluate_resilience_score_range(sample_component_code):
    """
    Verifies that evaluate_resilience_score produces an integer score strictly between 0 and 100
    under empty, flawed, and resilient component conditions.
    """
    dummy_suite = generate_chaos_suite(sample_component_code, mock=True)

    # 1. Empty code must score 0
    score_empty = evaluate_resilience_score("", dummy_suite)
    assert score_empty == 0

    # 2. Flawed component code
    score_flawed = evaluate_resilience_score(sample_component_code, dummy_suite)
    assert isinstance(score_flawed, int)
    assert 0 <= score_flawed <= 100

    # 3. Hardened, defensive code
    hardened_code = (
        "def safe_checkout(payload: dict):\n"
        "    try:\n"
        "        amount = payload.get('order', {}).get('total', 0.0)\n"
        "        sanitized = html.escape(str(amount))\n"
        "        style = 'width: 100%; max-width: 320px; overflow: hidden;'\n"
        "        return f'<button style=\"{style}\">{sanitized}</button>'\n"
        "    except (KeyError, TypeError, ValueError):\n"
        "        return '<button style=\"width: 100%;\">Error</button>'\n"
    )
    score_hardened = evaluate_resilience_score(hardened_code, dummy_suite)
    assert isinstance(score_hardened, int)
    assert 0 <= score_hardened <= 100
    assert score_hardened > score_flawed
