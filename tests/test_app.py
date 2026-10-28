"""
Unit tests for QA-Swarm app/main.py Streamlit dashboard.
Verifies script syntax, AST integrity, and core structure.
"""

import ast
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
APP_MAIN_PATH = PROJECT_ROOT / "app" / "main.py"


def test_app_main_exists_and_is_valid_ast():
    """
    Validates that app/main.py exists and parses cleanly with ast.parse (zero syntax errors).
    """
    assert APP_MAIN_PATH.exists(), f"Missing app file at: {APP_MAIN_PATH}"

    with open(APP_MAIN_PATH, "r", encoding="utf-8") as f:
        code = f.read()

    assert len(code) > 0
    parsed = ast.parse(code)
    assert parsed is not None


def test_app_main_contains_key_components():
    """
    Verifies that app/main.py contains key architectural components:
    set_page_config, run_full_audit, tabs, download buttons, and session state.
    """
    with open(APP_MAIN_PATH, "r", encoding="utf-8") as f:
        code = f.read()

    assert "st.set_page_config" in code
    assert "Load Demo Sample" in code
    assert "Run QA-Swarm Audit" in code
    assert "run_full_audit" in code
    assert "st.tabs" in code
    assert "st.metric" in code
    assert "export_to_sarif" in code
    assert "st.cache_data" in code
    assert "audit_result" in code
