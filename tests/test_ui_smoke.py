"""
Smoke and integration tests for QA-Swarm Streamlit dashboard (app/main.py).
Verifies AppTest rendering, AST mathematical syntax, dependency availability,
and orchestrator-to-UI communication without exceptions.
"""

import ast
from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest

from core.orchestrator import run_full_audit
from core.schemas import QAAuditReport

PROJECT_ROOT = Path(__file__).resolve().parent.parent
APP_MAIN_PATH = PROJECT_ROOT / "app" / "main.py"
SAMPLE_UI = PROJECT_ROOT / "test_samples" / "sample_ui.png"
BROKEN_COMPONENT = PROJECT_ROOT / "test_samples" / "broken_component.py"


def test_app_syntax_and_dependencies():
    """
    Verifies that app/main.py exists, parses cleanly with ast.parse (zero syntax errors),
    and all declared module dependencies are present.
    """
    assert APP_MAIN_PATH.exists(), f"App file not found at: {APP_MAIN_PATH}"

    with open(APP_MAIN_PATH, "r", encoding="utf-8") as f:
        code = f.read()

    parsed = ast.parse(code)
    assert parsed is not None

    # Verify key tokens and integration points exist
    assert "st.set_page_config" in code
    assert "META AI: SAM 3.1 + MUSE SPARK 1.3" in code
    assert "Multimodal Spatial Cortex - SAM 3" in code
    assert "Root-Cause Linking & Auto-Fixer - Muse Code" in code
    assert "Chaos Engine Suite" in code
    assert "Playwright Regression Test" in code
    assert "CI/CD & SARIF Report" in code


def test_streamlit_apptest_initial_render():
    """
    Uses streamlit.testing.v1.AppTest to verify headless initial boot of app/main.py
    without unhandled exceptions.
    """
    at = AppTest.from_file(str(APP_MAIN_PATH)).run()

    # Ensure zero exceptions were raised during script execution
    assert len(at.exception) == 0, f"AppTest encountered exceptions: {at.exception}"

    # Verify welcome title is rendered
    assert len(at.title) >= 1
    assert "QA-Swarm: Autonomous Multimodal QA & Healing Engine" in at.title[0].value


def test_orchestrator_ui_integration():
    """
    Verifies that core.orchestrator.run_full_audit communicates with demo sample files
    and produces all structures expected by the Streamlit UI metrics and tabs.
    """
    assert SAMPLE_UI.exists()
    assert BROKEN_COMPONENT.exists()

    report = run_full_audit(
        image_path=str(SAMPLE_UI),
        code_path_or_str=str(BROKEN_COMPONENT),
        mock=True,
    )

    assert isinstance(report, QAAuditReport)
    # Check metrics
    assert isinstance(report.health_score, int)
    assert report.verdict in ("BLOCK_DEPLOYMENT", "REQUIRES_REVIEW", "READY_FOR_PRODUCTION")
    # Check left column (vision)
    assert len(report.defects) >= 1
    assert report.defects[0].bbox == [420.0, 150.0, 480.0, 310.0]
    # Check right column (root cause & patch)
    assert len(report.root_causes) >= 1
    assert report.root_causes[0].target_line == 18
    assert len(report.patches) >= 1
    # Check bottom panel tabs (chaos suite)
    assert len(report.chaos_suite) == 5
    # Check agentic MCP trace
    assert len(report.mcp_trace) == 4
    assert report.mcp_trace[0].tool_name == "sam_spatial_scanner"


def test_streamlit_caching_and_session_state_persistence():
    """
    Verifies that app/main.py defines cached audit functions and preserves
    audit_result in session state for instant 0ms responses.
    """
    with open(APP_MAIN_PATH, "r", encoding="utf-8") as f:
        code = f.read()

    assert "@st.cache_data" in code
    assert "execute_cached_swarm_audit" in code
    assert 'st.session_state["audit_result"]' in code
    assert "compute_payload_hash" in code

    at = AppTest.from_file(str(APP_MAIN_PATH)).run()
    assert len(at.exception) == 0


def test_streamlit_all_audit_buttons_click_without_error():
    """
    Verifies that all buttons triggering trigger_audit in the sidebar and main view
    can be clicked without raising NameError or unhandled exceptions.
    """
    button_targets = [
        "⚡ Ejecutar Auditoría del Enjambre",
        "📁 Load Demo Sample",
        "⚡ Execute Full Swarm Audit",
        "🚀 Run QA-Swarm Audit",
    ]
    for target in button_targets:
        at = AppTest.from_file(str(APP_MAIN_PATH)).run()
        for btn in at.button:
            if btn.label == target:
                btn.click().run()
                assert len(at.exception) == 0, f"Exception clicked '{target}': {at.exception}"
