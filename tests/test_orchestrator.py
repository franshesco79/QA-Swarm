"""
Unit tests for QA-Swarm core/orchestrator.py and core/cli.py modules.
Verifies health scoring calculations, SARIF v2.1.0 compliance,
end-to-end audit orchestration, and CLI execution.
"""

import json
import os
from pathlib import Path
import subprocess
import sys
import pytest

from core.schemas import CodePatch, QAAuditReport, RootCauseLink, VisualDefect
from core.orchestrator import calculate_health_score, export_to_sarif, run_full_audit

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SAMPLE_UI = PROJECT_ROOT / "test_samples" / "sample_ui.png"
BROKEN_COMPONENT = PROJECT_ROOT / "test_samples" / "broken_component.py"


def test_calculate_health_score_scoring_logic():
    """
    Validates scoring deductions: critical defects and rigid styles yield BLOCK_DEPLOYMENT (< 60),
    whereas clean components yield READY_FOR_PRODUCTION (>= 80).
    """
    # Flawed component setup
    severe_defects = [
        VisualDefect(
            element_name="btn_purchase",
            bbox=[420.0, 150.0, 480.0, 310.0],
            defect_type="LAYOUT_OVERFLOW",
            severity="CRITICAL",
        )
    ]
    root_causes = [
        RootCauseLink(
            target_file="broken_component.py",
            target_line=18,
            offending_token="width: 120px",
            explanation="Rigid width causes layout overflow.",
        )
    ]
    flawed_score, flawed_verdict = calculate_health_score(
        defects=severe_defects,
        root_causes=root_causes,
        chaos_resilience=20,
    )
    assert flawed_score < 60
    assert flawed_verdict == "BLOCK_DEPLOYMENT"

    # Clean component setup
    clean_score, clean_verdict = calculate_health_score(
        defects=[],
        root_causes=[],
        chaos_resilience=95,
    )
    assert clean_score >= 80
    assert clean_verdict == "READY_FOR_PRODUCTION"


def test_export_to_sarif_schema_compliance():
    """
    Validates that export_to_sarif generates an OASIS SARIF v2.1.0 compliant JSON
    file with rules, schema, and non-empty results list.
    """
    report = run_full_audit(
        image_path=str(SAMPLE_UI),
        code_path_or_str=str(BROKEN_COMPONENT),
        mock=True,
    )

    output_sarif = PROJECT_ROOT / "test_samples" / "qa_audit.sarif"
    if output_sarif.exists():
        output_sarif.unlink()

    sarif_path = export_to_sarif(report, str(output_sarif))

    assert os.path.exists(sarif_path)
    assert os.path.getsize(sarif_path) > 0

    with open(sarif_path, "r", encoding="utf-8") as f:
        sarif_json = json.load(f)

    # Specification checks
    assert sarif_json.get("version") == "2.1.0"
    assert "sarif-schema-2.1.0.json" in sarif_json.get("$schema", "")
    runs = sarif_json.get("runs", [])
    assert len(runs) >= 1

    driver = runs[0].get("tool", {}).get("driver", {})
    assert driver.get("name") == "QA-Swarm"
    assert len(driver.get("rules", [])) >= 1

    results = runs[0].get("results", [])
    assert len(results) >= 1
    first_res = results[0]
    assert "ruleId" in first_res
    assert "level" in first_res
    assert "message" in first_res
    assert "locations" in first_res


def test_run_full_audit_pipeline():
    """
    Validates that run_full_audit executes the end-to-end pipeline and returns
    a fully populated, valid QAAuditReport instance.
    """
    report = run_full_audit(
        image_path=str(SAMPLE_UI),
        code_path_or_str=str(BROKEN_COMPONENT),
        mock=True,
    )

    assert isinstance(report, QAAuditReport)
    assert 0 <= report.health_score <= 100
    assert report.verdict in ("BLOCK_DEPLOYMENT", "REQUIRES_REVIEW", "READY_FOR_PRODUCTION")

    # Verify all subsystems populated data
    assert len(report.defects) >= 1
    assert len(report.root_causes) >= 1
    assert len(report.patches) >= 1
    assert len(report.chaos_suite) == 5

    # Check first patch and root cause consistency
    assert report.root_causes[0].target_line == 18
    assert "width: 100%" in report.patches[0].replacement_snippet


def test_cli_execution():
    """
    Validates programmatic execution of core.cli via subprocess.run,
    verifying ANSI summary rendering, SARIF generation, and CI/CD exit codes.
    """
    sarif_output = PROJECT_ROOT / "test_samples" / "cli_test_audit.sarif"
    if sarif_output.exists():
        sarif_output.unlink()

    # 1. Test CLI with --allow-blocked (should succeed with exit code 0)
    cmd_allow = [
        sys.executable,
        "-m",
        "core.cli",
        "--ui",
        str(SAMPLE_UI),
        "--code",
        str(BROKEN_COMPONENT),
        "--sarif",
        str(sarif_output),
        "--mock",
        "--allow-blocked",
    ]

    res_allow = subprocess.run(
        cmd_allow,
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )

    assert res_allow.returncode == 0, f"CLI failed: {res_allow.stderr}"
    assert "QA-SWARM AUTOMATED MULTIMODAL AUDIT REPORT" in res_allow.stdout
    assert "System Health Score:" in res_allow.stdout
    assert "Deployment Verdict" in res_allow.stdout
    assert os.path.exists(sarif_output)
    assert os.path.getsize(sarif_output) > 0

    # 2. Test CLI without --allow-blocked (should block deployment with exit code 1)
    cmd_block = [
        sys.executable,
        "-m",
        "core.cli",
        "--ui",
        str(SAMPLE_UI),
        "--code",
        str(BROKEN_COMPONENT),
        "--mock",
    ]

    res_block = subprocess.run(
        cmd_block,
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )

    assert res_block.returncode == 1
    assert "BLOCK_DEPLOYMENT" in res_block.stdout
