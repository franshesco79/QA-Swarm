"""
Unit tests for QA-Swarm core/analyzer.py module.
Verifies source code root cause analysis, patch generation, patch application,
and unified diff generation.
"""

from pathlib import Path
import pytest

from core.schemas import CodePatch, RootCauseLink
from core.analyzer import (
    analyze_source_code,
    generate_code_patch,
    apply_patch_to_code,
    generate_diff_view,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BROKEN_COMPONENT_PATH = PROJECT_ROOT / "test_samples" / "broken_component.py"


def test_analyze_source_code_mock():
    """
    Validates that analyze_source_code with mock=True returns at least one RootCauseLink
    with the expected target_line and offending_token.
    """
    assert BROKEN_COMPONENT_PATH.exists(), f"Component file missing: {BROKEN_COMPONENT_PATH}"

    root_causes = analyze_source_code(str(BROKEN_COMPONENT_PATH), mock=True)

    assert isinstance(root_causes, list)
    assert len(root_causes) >= 1

    rc = root_causes[0]
    assert isinstance(rc, RootCauseLink)
    assert rc.target_line == 18
    assert "width: 120px" in rc.offending_token
    assert len(rc.explanation) > 0


def test_generate_code_patch_schema():
    """
    Validates that generate_code_patch returns a valid CodePatch instance
    conforming strictly to Pydantic schemas.
    """
    rc = RootCauseLink(
        target_file="broken_component.py",
        target_line=18,
        offending_token="width: 120px",
        explanation="Rigid width causes layout overflow.",
    )

    with open(BROKEN_COMPONENT_PATH, "r", encoding="utf-8") as f:
        source_code = f.read()

    patch = generate_code_patch(source_code, rc, mock=True)

    assert isinstance(patch, CodePatch)
    assert patch.target_file == "broken_component.py"
    assert patch.target_line == 18
    assert "width: 120px;" in patch.original_snippet or "width: 120px" in patch.original_snippet
    assert "width: 100%;" in patch.replacement_snippet or "width: 100%" in patch.replacement_snippet


def test_apply_patch_correctness():
    """
    Validates that applying a patch modifies the targeted line correctly without duplicating lines.
    """
    sample_code = (
        "def render():\n"
        "    btn_id = 'purchase'\n"
        '    style = "width: 120px;"\n'
        "    return style\n"
    )

    patch = CodePatch(
        target_file="component.py",
        target_line=3,
        original_snippet='width: 120px;',
        replacement_snippet='width: 100%;',
    )

    original_line_count = len(sample_code.splitlines())
    patched_code = apply_patch_to_code(sample_code, patch)
    patched_line_count = len(patched_code.splitlines())

    # Line count must remain identical
    assert patched_line_count == original_line_count
    # Original text must be gone, new text must be present
    assert "width: 120px;" not in patched_code
    assert "width: 100%;" in patched_code
    # Indentation preserved
    assert '    style = "width: 100%;"\n' in patched_code


def test_generate_diff_contains_markers():
    """
    Validates that generate_diff_view returns a unified diff with '+' and '-' markers.
    """
    orig_code = 'style = "width: 120px;"\nreturn style'
    patched_code = 'style = "width: 100%;"\nreturn style'

    diff_output = generate_diff_view(orig_code, patched_code)

    assert isinstance(diff_output, str)
    assert len(diff_output) > 0
    assert "--- original" in diff_output
    assert "+++ patched" in diff_output
    assert "-" in diff_output
    assert "+" in diff_output
    assert "-style = \"width: 120px;\"" in diff_output
    assert "+style = \"width: 100%;\"" in diff_output
