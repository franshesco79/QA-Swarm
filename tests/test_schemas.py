"""
Unit tests for QA-Swarm Phase 1 schemas and client.
Includes tests for Meta AI SAM 3.1 and Muse Spark 1.3 client integration.
"""

from core.schemas import CodePatch, QAAuditReport, RootCauseLink, VisualDefect
from core.client import QASwarmClient, SAM3_BOX_PATTERN


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


def test_client_call_sam3_vision_fallback():
    client = QASwarmClient()
    defects = client.call_sam3_vision()
    assert isinstance(defects, list)
    assert len(defects) >= 1
    assert isinstance(defects[0], VisualDefect)
    assert defects[0].bbox == [420.0, 150.0, 480.0, 310.0]


def test_client_call_muse_spark_correlation_fallback():
    client = QASwarmClient()
    root_causes, patches = client.call_muse_spark_correlation(
        source_code='style = "width: 120px;"',
        defects=[VisualDefect(element_name="btn", bbox=[420.0, 150.0, 480.0, 310.0])],
    )
    assert isinstance(root_causes, list)
    assert isinstance(patches, list)
    assert len(root_causes) >= 1
    assert isinstance(root_causes[0], RootCauseLink)
    assert isinstance(patches[0], CodePatch)


def test_client_sam3_box_regex_parsing():
    sample_token = "<|box;x1=150;y1=420;x2=310;y2=480;w=800;h=600|>"
    match = SAM3_BOX_PATTERN.search(sample_token)
    assert match is not None
    x1, y1, x2, y2, w, h = match.groups()
    ymin, xmin = float(y1), float(x1)
    ymax, xmax = float(y2), float(x2)
    bbox = [ymin, xmin, ymax, xmax]
    assert bbox == [420.0, 150.0, 480.0, 310.0]
