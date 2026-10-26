"""
Unit tests for QA-Swarm core/correlator.py module.
Verifies multimodal linking from visual defects to source code lines,
batch defect correlation consistency, and graceful fallback on empty/corrupt code.
"""

from pathlib import Path
import pytest

from core.schemas import RootCauseLink, VisualDefect
from core.correlator import correlate_visual_to_code, correlate_all_defects

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BROKEN_COMPONENT_PATH = PROJECT_ROOT / "test_samples" / "broken_component.py"


@pytest.fixture
def sample_source_code() -> str:
    assert BROKEN_COMPONENT_PATH.exists(), f"Missing file: {BROKEN_COMPONENT_PATH}"
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


def test_correlate_single_defect_mock(sample_defect, sample_source_code):
    """
    Verifies that correlate_visual_to_code returns a RootCauseLink pointing to line 18
    and a valid target_file.
    """
    link = correlate_visual_to_code(
        defect=sample_defect,
        source_code=sample_source_code,
        file_name="broken_component.py",
        mock=True,
    )

    assert isinstance(link, RootCauseLink)
    assert link.target_file == "broken_component.py"
    assert link.target_line == 18
    assert "width: 120px" in link.offending_token
    assert len(link.explanation) > 0


def test_correlate_all_defects_consistency(sample_source_code):
    """
    Verifies that a list of N defects produces exactly N validated RootCauseLink instances.
    """
    defects = [
        VisualDefect(
            element_name="btn_purchase",
            bbox=[420.0, 150.0, 480.0, 310.0],
            defect_type="LAYOUT_OVERFLOW",
            severity="CRITICAL",
        ),
        VisualDefect(
            element_name="card_container",
            bbox=[100.0, 120.0, 530.0, 700.0],
            defect_type="CONTAINER_CLIPPING",
            severity="WARNING",
        ),
        VisualDefect(
            element_name="footer_badge",
            bbox=[550.0, 50.0, 590.0, 200.0],
            defect_type="TEXT_TRUNCATION",
            severity="LOW",
        ),
    ]

    source_files = {
        "broken_component.py": sample_source_code,
        "container.py": "def render_card(): pass",
    }

    links = correlate_all_defects(defects, source_files, mock=True)

    assert isinstance(links, list)
    assert len(links) == len(defects) == 3

    for link in links:
        assert isinstance(link, RootCauseLink)
        assert link.target_line >= 1
        assert len(link.target_file) > 0
        assert len(link.offending_token) > 0
        assert len(link.explanation) > 0


def test_correlate_empty_code_graceful_fallback(sample_defect):
    """
    Verifies that empty or corrupt source code does not raise unhandled exceptions
    and returns a graceful contingency RootCauseLink.
    """
    # Test with empty string and whitespace
    for empty_input in ["", "   \n\t  "]:
        # Test both mock=True and mock=False paths
        for mock_flag in [True, False]:
            link = correlate_visual_to_code(
                defect=sample_defect,
                source_code=empty_input,
                file_name="corrupt_component.py",
                mock=mock_flag,
            )

            assert isinstance(link, RootCauseLink)
            assert link.target_file == "corrupt_component.py"
            assert link.target_line == 1
            assert "Contingency" in link.explanation or "empty" in link.explanation.lower()
            assert link.offending_token == "EMPTY_OR_CORRUPT_SOURCE"
