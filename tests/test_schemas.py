"""
Unit tests for QA-Swarm Phase 1 schemas and client.
"""

from core.schemas import QAAuditReport
from core.client import QASwarmClient


def test_mock_audit_json_validity():
    client = QASwarmClient()
    report = client.load_mock_audit_report()
    assert isinstance(report, QAAuditReport)
    assert report.health_score == 42
    assert report.verdict == "BLOCK_DEPLOYMENT"
    assert len(report.defects) == 1
    assert report.defects[0].bbox == [420.0, 150.0, 480.0, 310.0]
    assert report.root_causes[0].target_file == "component.py"
    assert report.root_causes[0].target_line == 18
    assert report.patches[0].replacement_snippet == "width: 100%;"
    assert len(report.chaos_suite) == 5


def test_client_run_audit_fallback():
    client = QASwarmClient()
    report = client.run_audit(target_url="http://localhost:8501")
    assert report.verdict == "BLOCK_DEPLOYMENT"
