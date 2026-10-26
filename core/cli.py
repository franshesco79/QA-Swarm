"""
CLI Runner for QA-Swarm.
Provides command-line execution and CI/CD integration for automated UI/code audits,
health scoring, and SARIF export.
"""

import argparse
import os
import sys
from pathlib import Path

from core.orchestrator import export_to_sarif, run_full_audit


# ANSI Colors for CI/CD terminal formatting
class ANSI:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"


def format_summary(report, sarif_path: str) -> str:
    lines = []
    lines.append(f"{ANSI.BOLD}{ANSI.CYAN}{'=' * 72}{ANSI.RESET}")
    lines.append(f"{ANSI.BOLD}{ANSI.CYAN}       QA-SWARM AUTOMATED MULTIMODAL AUDIT REPORT{ANSI.RESET}")
    lines.append(f"{ANSI.BOLD}{ANSI.CYAN}{'=' * 72}{ANSI.RESET}\n")

    # Verdict & Score
    if report.health_score >= 80:
        score_color = ANSI.GREEN
    elif report.health_score >= 60:
        score_color = ANSI.YELLOW
    else:
        score_color = ANSI.RED

    lines.append(
        f"  {ANSI.BOLD}System Health Score:{ANSI.RESET} {score_color}{report.health_score}/100{ANSI.RESET}"
    )
    lines.append(
        f"  {ANSI.BOLD}Deployment Verdict :{ANSI.RESET} {score_color}{report.verdict}{ANSI.RESET}\n"
    )

    # Defects
    lines.append(f"  {ANSI.BOLD}Visual Defects Detected ({len(report.defects)}):{ANSI.RESET}")
    for idx, defect in enumerate(report.defects, 1):
        lines.append(
            f"    [{idx}] {ANSI.RED}{defect.element_name}{ANSI.RESET} "
            f"type={defect.defect_type} severity={defect.severity} bbox={defect.bbox}"
        )

    # Root Causes & Patches
    lines.append(f"\n  {ANSI.BOLD}Root Causes & Patches ({len(report.root_causes)}):{ANSI.RESET}")
    for idx, (rc, patch) in enumerate(zip(report.root_causes, report.patches), 1):
        lines.append(
            f"    [{idx}] {rc.target_file}:{rc.target_line} [{ANSI.YELLOW}{rc.offending_token}{ANSI.RESET}]"
        )
        lines.append(f"        Explanation: {rc.explanation}")
        lines.append(
            f"        Remediation: {ANSI.GREEN}{patch.original_snippet} -> {patch.replacement_snippet}{ANSI.RESET}"
        )

    # Chaos Suite
    lines.append(f"\n  {ANSI.BOLD}Chaos Resilience Suite ({len(report.chaos_suite)} vectors):{ANSI.RESET}")
    for idx, case in enumerate(report.chaos_suite, 1):
        lines.append(
            f"    [{idx}] {case.test_id} [{ANSI.BLUE}{case.stress_vector}{ANSI.RESET}]"
        )

    lines.append(f"\n  {ANSI.BOLD}SARIF v2.1.0 Export:{ANSI.RESET} {sarif_path}")
    lines.append(f"{ANSI.BOLD}{ANSI.CYAN}{'=' * 72}{ANSI.RESET}\n")
    return "\n".join(lines)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="QA-Swarm CLI: Autonomous Multimodal QA & CI/CD Gate Engine"
    )
    parser.add_argument(
        "--ui",
        type=str,
        default="test_samples/sample_ui.png",
        help="Path to UI screenshot image (default: test_samples/sample_ui.png)",
    )
    parser.add_argument(
        "--code",
        type=str,
        default="test_samples/broken_component.py",
        help="Path to target source code file (default: test_samples/broken_component.py)",
    )
    parser.add_argument(
        "--sarif",
        type=str,
        default="test_samples/qa_audit.sarif",
        help="Output path for SARIF v2.1.0 report (default: test_samples/qa_audit.sarif)",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        default=True,
        help="Use deterministic mock data (default: True)",
    )
    parser.add_argument(
        "--no-mock",
        dest="mock",
        action="store_false",
        help="Disable mock mode and use live agent/inference endpoints",
    )
    parser.add_argument(
        "--allow-blocked",
        action="store_true",
        default=False,
        help="Exit with 0 even if verdict is BLOCK_DEPLOYMENT (for CI inspection)",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    # Run complete audit pipeline
    report = run_full_audit(
        image_path=args.ui,
        code_path_or_str=args.code,
        mock=args.mock,
    )

    # Export SARIF
    sarif_path = export_to_sarif(report, args.sarif)

    # Print summary
    print(format_summary(report, sarif_path))

    # Exit code based on verdict
    if report.verdict == "BLOCK_DEPLOYMENT" and not args.allow_blocked:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
