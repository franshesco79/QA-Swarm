"""
Swarm Orchestrator and SARIF v2.1.0 Exporter for QA-Swarm.
Coordinates multimodal vision inspection, code correlation, patch generation,
adversarial chaos evaluation, health scoring, and CI/CD reporting.
"""

import json
import logging
from pathlib import Path
from typing import List, Tuple

from core.schemas import CodePatch, QAAuditReport, RootCauseLink, VisualDefect
from core.vision import draw_bounding_boxes, inspect_ui_elements
from core.correlator import correlate_all_defects
from core.analyzer import generate_code_patch
from core.chaos import evaluate_resilience_score, generate_chaos_suite
from core.test_generator import generate_playwright_test, save_generated_test

logger = logging.getLogger("qa_swarm.orchestrator")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SARIF_OUTPUT = PROJECT_ROOT / "test_samples" / "qa_audit.sarif"


def calculate_health_score(
    defects: List[VisualDefect],
    root_causes: List[RootCauseLink],
    chaos_resilience: int,
) -> Tuple[int, str]:
    """
    Computes a composite system health score between 0 and 100 and emits a categorical verdict:
    - Deductions:
      * Critical / severe layout overflow: -25 pts
      * Visual warnings / minor layout defects: -15 pts
      * Rigid code constraints / unhandled logic: -10 pts
    - Combines visual/code deductions (70% weight) with chaos resilience (30% weight).
    - Verdict:
      * < 60: BLOCK_DEPLOYMENT
      * 60 - 79: REQUIRES_REVIEW
      * >= 80: READY_FOR_PRODUCTION
    """
    base_score = 100
    deductions = 0

    # 1. Defect deductions
    for defect in defects:
        severity = defect.severity.upper()
        if severity in ("CRITICAL", "HIGH") or defect.defect_type == "LAYOUT_OVERFLOW":
            deductions += 25
        else:
            deductions += 15

    # 2. Root cause deductions
    for rc in root_causes:
        token = rc.offending_token.lower()
        if any(kw in token for kw in ["width:", "120px", "height:", "px", "fixed"]):
            deductions += 10
        else:
            deductions += 5

    visual_code_score = max(0, base_score - deductions)

    # 3. Weighted composite calculation (70% visual/code, 30% chaos resilience)
    chaos_score = max(0, min(100, chaos_resilience))
    composite_score = int(round(0.70 * visual_code_score + 0.30 * chaos_score))
    final_score = max(0, min(100, composite_score))

    # 4. Categorical verdict
    if final_score < 60:
        verdict = "BLOCK_DEPLOYMENT"
    elif final_score < 80:
        verdict = "REQUIRES_REVIEW"
    else:
        verdict = "READY_FOR_PRODUCTION"

    return final_score, verdict


def export_to_sarif(
    report: QAAuditReport,
    output_path: str = "test_samples/qa_audit.sarif",
) -> str:
    """
    Generates a valid OASIS SARIF v2.1.0 JSON report suitable for GitHub Code Scanning
    and CI/CD security/quality gates.
    """
    resolved_path = Path(output_path).resolve()
    resolved_path.parent.mkdir(parents=True, exist_ok=True)

    rules = [
        {
            "id": "QA-SWARM-VIS-001",
            "name": "VisualLayoutOverflow",
            "shortDescription": {"text": "UI component exceeds container layout boundaries."},
            "defaultConfiguration": {"level": "error"},
        },
        {
            "id": "QA-SWARM-CODE-001",
            "name": "RigidDimensionConstraint",
            "shortDescription": {"text": "Hardcoded dimension causes component layout overflow."},
            "defaultConfiguration": {"level": "warning"},
        },
    ]

    results = []

    # Map visual defects to SARIF results
    for defect in report.defects:
        rule_id = (
            "QA-SWARM-VIS-001"
            if defect.defect_type == "LAYOUT_OVERFLOW"
            else f"QA-SWARM-VIS-{defect.defect_type}"
        )
        level = "error" if defect.severity.upper() in ("CRITICAL", "HIGH") else "warning"

        target_file = report.root_causes[0].target_file if report.root_causes else "broken_component.py"
        target_line = report.root_causes[0].target_line if report.root_causes else 1

        results.append({
            "ruleId": rule_id,
            "level": level,
            "message": {
                "text": (
                    f"Visual defect '{defect.defect_type}' detected on element '{defect.element_name}' "
                    f"at coordinates {defect.bbox} with severity '{defect.severity}'."
                )
            },
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {"uri": target_file},
                        "region": {"startLine": target_line},
                    }
                }
            ],
        })

    # Map root causes to SARIF results
    for rc in report.root_causes:
        results.append({
            "ruleId": "QA-SWARM-CODE-001",
            "level": "warning",
            "message": {
                "text": f"Root Cause: {rc.explanation} [Token: '{rc.offending_token}']"
            },
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {"uri": rc.target_file},
                        "region": {"startLine": rc.target_line},
                    }
                }
            ],
        })

    sarif_data = {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "QA-Swarm",
                        "version": "1.0.0",
                        "informationUri": "https://github.com/meta-hackathon/qa-swarm",
                        "rules": rules,
                    }
                },
                "results": results,
            }
        ],
    }

    with open(resolved_path, "w", encoding="utf-8") as f:
        json.dump(sarif_data, f, indent=2)

    return str(resolved_path)


def run_full_audit(
    image_path: str,
    code_path_or_str: str,
    file_name: str = "broken_component.py",
    mock: bool = True,
) -> QAAuditReport:
    """
    Executes the complete multimodal end-to-end QA-Swarm pipeline:
    1. UI inspection & bounding box drawing
    2. Code correlation & root cause identification
    3. Automated code patch synthesis
    4. Chaos Engine test suite generation & resilience evaluation
    5. Playwright regression test synthesis
    6. Health Score & Verdict determination
    7. Validation into a unified QAAuditReport
    """
    # 1. Resolve source code and filename
    code_path = Path(code_path_or_str)
    if code_path.exists() and code_path.is_file():
        file_name = code_path.name
        with open(code_path, "r", encoding="utf-8") as f:
            source_code = f.read()
    else:
        source_code = code_path_or_str

    # 2. Inspect UI Elements & annotate image
    defects = inspect_ui_elements(image_path=image_path, mock=mock)
    draw_bounding_boxes(image_path=image_path, defects=defects)

    # 3. Correlate visual defects with code lines
    source_files = {file_name: source_code}
    root_causes = correlate_all_defects(defects=defects, source_files=source_files, mock=mock)

    # 4. Generate Code Patches
    patches: List[CodePatch] = []
    for rc in root_causes:
        patch = generate_code_patch(source_code=source_code, root_cause=rc, mock=mock)
        patches.append(patch)

    # 5. Synthesize Chaos Test Suite & compute resilience
    primary_defect = defects[0] if defects else None
    chaos_suite = generate_chaos_suite(
        component_code=source_code,
        defect=primary_defect,
        mock=mock,
    )
    resilience_score = evaluate_resilience_score(source_code, chaos_suite)

    # 6. Generate Playwright Regression Test
    if defects and patches:
        playwright_code = generate_playwright_test(
            defect=defects[0],
            patch=patches[0],
            mock=mock,
        )
        save_generated_test(playwright_code)

    # 7. Compute Health Score and Verdict
    health_score, verdict = calculate_health_score(
        defects=defects,
        root_causes=root_causes,
        chaos_resilience=resilience_score,
    )

    # 8. Assemble and return validated QAAuditReport
    report = QAAuditReport(
        health_score=health_score,
        verdict=verdict,
        defects=defects,
        root_causes=root_causes,
        patches=patches,
        chaos_suite=chaos_suite,
    )

    return report
