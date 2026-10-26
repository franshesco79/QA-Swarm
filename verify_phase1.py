"""
Verification script for Phase 1 of QA-Swarm.
Validates Pydantic v2 schema conformity against mock_audit_result.json
and tests QASwarmClient deterministic fallback.
"""

import sys
import json
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.schemas import QAAuditReport, VisualDefect, RootCauseLink, CodePatch, ChaosTestCase
from core.client import QASwarmClient


def run_verification():
    print("=" * 70)
    print("QA-SWARM [FASE 1]: VERIFICACIÓN DE ESQUEMAS Y CLIENTE MOCK")
    print("=" * 70)

    mock_json_path = PROJECT_ROOT / "test_samples" / "mock_audit_result.json"
    assert mock_json_path.exists(), f"Mock JSON file not found at: {mock_json_path}"

    # 1. Direct JSON Validation with Pydantic
    print("\n[Paso 1] Validando JSON mock directamente con QAAuditReport...")
    with open(mock_json_path, "r", encoding="utf-8") as f:
        raw_json = json.load(f)

    report = QAAuditReport.model_validate(raw_json)
    print(f" -> Reporte parseado exitosamente.")
    print(f" -> Health Score: {report.health_score}/100")
    print(f" -> Veredicto: {report.verdict}")
    print(f" -> Defectos visuales: {len(report.defects)}")
    print(f" -> Causas raíz: {len(report.root_causes)}")
    print(f" -> Parches: {len(report.patches)}")
    print(f" -> Casos Chaos Suite: {len(report.chaos_suite)}")

    # Specific criteria checks
    assert report.health_score == 42, f"Expected health_score 42, got {report.health_score}"
    assert report.verdict == "BLOCK_DEPLOYMENT", f"Expected BLOCK_DEPLOYMENT, got {report.verdict}"

    # Visual Defect check
    assert len(report.defects) >= 1, "Must have at least 1 visual defect"
    defect = report.defects[0]
    assert defect.bbox == [420.0, 150.0, 480.0, 310.0], f"Unexpected bbox: {defect.bbox}"
    print(f" -> Defecto visual validado: {defect.element_name} @ {defect.bbox} ({defect.severity})")

    # Root Cause check
    assert len(report.root_causes) >= 1, "Must have at least 1 root cause"
    rc = report.root_causes[0]
    assert rc.target_file == "component.py", f"Expected component.py, got {rc.target_file}"
    assert rc.target_line == 18, f"Expected line 18, got {rc.target_line}"
    assert "width: 120px" in rc.offending_token, f"Unexpected token: {rc.offending_token}"
    print(f" -> Causa raíz validada: {rc.target_file}:{rc.target_line} [{rc.offending_token}]")

    # Patch check
    assert len(report.patches) >= 1, "Must have at least 1 patch"
    patch = report.patches[0]
    assert patch.target_file == "component.py"
    assert patch.target_line == 18
    assert "width: 100%" in patch.replacement_snippet, f"Unexpected patch replacement: {patch.replacement_snippet}"
    print(f" -> Parche validado: {patch.original_snippet} -> {patch.replacement_snippet}")

    # Chaos suite check
    assert len(report.chaos_suite) == 5, f"Expected exactly 5 chaos test cases, got {len(report.chaos_suite)}"
    for idx, case in enumerate(report.chaos_suite, 1):
        print(f"    - Chaos {idx}: [{case.test_id}] {case.stress_vector} -> {case.expected_behavior[:50]}...")

    # 2. Testing QASwarmClient
    print("\n[Paso 2] Validando QASwarmClient con USE_MOCK / Fallback determinista...")
    client = QASwarmClient()
    client_report = client.run_audit(target_url="http://localhost:8501")
    assert isinstance(client_report, QAAuditReport)
    assert client_report.health_score == 42
    print(" -> QASwarmClient ejecutó run_audit() y retornó QAAuditReport determinista sin llamadas de red.")

    print("\n" + "=" * 70)
    print("TODAS LAS VERIFICACIONES DE LA FASE 1 COMPLETADAS CON ÉXITO (0 ERRORES).")
    print("=" * 70)


if __name__ == "__main__":
    run_verification()
