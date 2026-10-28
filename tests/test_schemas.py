"""
Unit tests for QA-Swarm Phase 1 schemas and client.
Includes tests for Meta AI SAM 3.1 and Muse Spark 1.3 client integration.
"""

import base64
import io
from pathlib import Path
from PIL import Image

from core.schemas import CodePatch, QAAuditReport, RootCauseLink, SwarmAuditResult, VisualDefect
from core.client import QASwarmClient, SAM3_BOX_PATTERN, optimize_and_encode_image


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
    assert len(report.mcp_trace) == 4
    assert report.mcp_trace[0].model_used == "sam-3.1"
    assert report.mcp_trace[1].model_used == "muse-spark-1.3"


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


def test_swarm_audit_result_alias():
    assert SwarmAuditResult is QAAuditReport


def test_optimize_and_encode_image_resizes_large_image():
    test_img_path = Path(__file__).resolve().parent.parent / "test_samples" / "temp_large_test.png"
    try:
        img = Image.new("RGB", (1920, 1080), color=(100, 150, 200))
        img.save(test_img_path, format="PNG")

        b64_str = optimize_and_encode_image(test_img_path, max_width=1280)
        assert isinstance(b64_str, str)
        assert len(b64_str) > 0

        decoded_bytes = base64.b64decode(b64_str)
        with Image.open(io.BytesIO(decoded_bytes)) as decoded_img:
            assert decoded_img.width == 1280
            assert decoded_img.height == 720
    finally:
        if test_img_path.exists():
            test_img_path.unlink()


def test_client_connection_pool_session():
    client = QASwarmClient()
    assert hasattr(client, "_session")
    assert client._session.headers.get("Connection") == "keep-alive"
    client.close()
