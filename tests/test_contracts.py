"""
Contract and schema integration tests for QA-Swarm.
Validates agentic MCP execution traces, Model Context Protocol tool contracts,
and Playwright resilient browser capture contracts.
"""

from pathlib import Path
import pytest

from core.browser import capture_url_screenshot
from core.cli import parse_args
from core.orchestrator import run_full_audit
from core.schemas import MCPToolTrace, QAAuditReport, SwarmAuditResult

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SAMPLE_UI = PROJECT_ROOT / "test_samples" / "sample_ui.png"
BROKEN_COMPONENT = PROJECT_ROOT / "test_samples" / "broken_component.py"


def test_mcp_trace_contract_and_model_references():
    """
    Validates that run_full_audit produces an aggregate report conforming to SwarmAuditResult,
    with mcp_trace containing all 4 orchestrated agentic tools and exact model identifiers
    (sam-3.1 and muse-spark-1.3).
    """
    report = run_full_audit(
        image_path=str(SAMPLE_UI),
        code_path_or_str=str(BROKEN_COMPONENT),
        mock=True,
    )

    assert isinstance(report, SwarmAuditResult)
    assert isinstance(report.mcp_trace, list)
    assert len(report.mcp_trace) == 4

    expected_tools = [
        ("sam_spatial_scanner", "sam-3.1"),
        ("muse_spark_causal_correlator", "muse-spark-1.3"),
        ("chaos_stress_engine", "chaos-engine"),
        ("sarif_gate_exporter", "sarif-v2.1.0"),
    ]

    for idx, (expected_tool, expected_model) in enumerate(expected_tools, 1):
        trace: MCPToolTrace = report.mcp_trace[idx - 1]
        assert isinstance(trace, MCPToolTrace)
        assert trace.step == idx
        assert trace.tool_name == expected_tool
        assert trace.model_used == expected_model
        assert trace.status in ("SUCCESS", "FALLBACK")
        assert trace.latency_ms >= 0
        assert len(trace.summary) > 0


def test_capture_url_screenshot_safe_failure_handling():
    """
    Validates that capture_url_screenshot handles network/browser failures safely
    by falling back to sample_ui.png without raising unhandled exceptions when fallback_on_error=True.
    """
    temp_target = PROJECT_ROOT / "test_samples" / "temp_contract_capture.png"
    try:
        fallback_result = capture_url_screenshot(
            url="http://invalid.contract.test.domain:9999",
            output_path=str(temp_target),
            timeout_ms=1000,
            fallback_on_error=True,
        )
        assert Path(fallback_result).exists()
        assert Path(fallback_result).stat().st_size > 0

        # When fallback_on_error is False, it should raise RuntimeError cleanly
        with pytest.raises(RuntimeError):
            capture_url_screenshot(
                url="http://invalid.contract.test.domain:9999",
                output_path=str(temp_target),
                timeout_ms=1000,
                fallback_on_error=False,
            )
    finally:
        if temp_target.exists():
            temp_target.unlink()


def test_cli_live_url_argument_parsing():
    """
    Validates that CLI parser accepts --url and routes to live URL capture.
    """
    args = parse_args(["--url", "https://example.com/live-demo"])
    assert args.url == "https://example.com/live-demo"
    assert args.ui == "test_samples/sample_ui.png"
