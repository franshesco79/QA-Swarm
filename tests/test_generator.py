"""
Unit tests for QA-Swarm core/test_generator.py module.
Verifies Playwright regression test synthesis, AST mathematical syntax validation,
syntax error detection, and disk serialization.
"""

import os
from pathlib import Path
import pytest

from core.schemas import CodePatch, VisualDefect
from core.test_generator import (
    generate_playwright_test,
    validate_test_syntax,
    save_generated_test,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def sample_defect() -> VisualDefect:
    return VisualDefect(
        element_name="btn_purchase",
        bbox=[420.0, 150.0, 480.0, 310.0],
        defect_type="LAYOUT_OVERFLOW",
        severity="CRITICAL",
    )


@pytest.fixture
def sample_patch() -> CodePatch:
    return CodePatch(
        target_file="broken_component.py",
        target_line=18,
        original_snippet="width: 120px;",
        replacement_snippet="width: 100%;",
    )


def test_generate_playwright_test_structure(sample_defect, sample_patch):
    """
    Validates that the synthesized script contains all mandatory Playwright components,
    assertions, and target element identifiers.
    """
    script = generate_playwright_test(
        defect=sample_defect,
        patch=sample_patch,
        target_url="http://localhost:8501",
        mock=True,
    )

    assert isinstance(script, str)
    assert len(script) > 0

    # Key import and initialization markers
    assert "playwright.sync_api" in script
    assert "sync_playwright" in script
    assert "expect" in script or "assert" in script

    # Element and regression target markers
    assert sample_defect.element_name in script
    assert "scrollWidth" in script
    assert "clientWidth" in script
    assert "try:" in script
    assert "finally:" in script
    assert "browser.close()" in script


def test_generated_test_is_valid_python_ast(sample_defect, sample_patch):
    """
    Validates that validate_test_syntax confirms the generated script
    is 100% syntactically correct Python via AST parsing.
    """
    script = generate_playwright_test(
        defect=sample_defect,
        patch=sample_patch,
        target_url="http://localhost:8501",
        mock=True,
    )

    is_valid = validate_test_syntax(script)
    assert is_valid is True


def test_validate_test_syntax_detects_syntax_errors():
    """
    Validates that validate_test_syntax reliably catches SyntaxError
    and returns False without throwing unhandled exceptions.
    """
    invalid_code = "def broken_func(:\n    pass"
    is_valid = validate_test_syntax(invalid_code)
    assert is_valid is False

    empty_code = ""
    assert validate_test_syntax(empty_code) is True  # Empty module is valid AST in Python

    bad_indent = "def foo():\nreturn 1"
    assert validate_test_syntax(bad_indent) is False


def test_save_generated_test_writes_file(sample_defect, sample_patch):
    """
    Validates that save_generated_test verifies syntax, saves to disk,
    and creates a non-empty file.
    """
    script = generate_playwright_test(sample_defect, sample_patch)
    output_target = PROJECT_ROOT / "test_samples" / "test_regression.py"

    if output_target.exists():
        output_target.unlink()

    saved_path = save_generated_test(script, str(output_target))

    assert os.path.exists(saved_path)
    assert os.path.isfile(saved_path)
    assert os.path.getsize(saved_path) > 0
    assert str(output_target.resolve()) == str(Path(saved_path).resolve())

    # Ensure saved content matches generated script
    with open(saved_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert sample_defect.element_name in content
    assert "playwright.sync_api" in content
