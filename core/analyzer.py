"""
Static Code Analyzer, Root Cause Identifier, and Automated Patching Engine for QA-Swarm.
Provides deterministic static analysis fallback, automated CodePatch generation,
code remediation, and unified diff view generation using difflib.
"""

import difflib
import json
import os
from pathlib import Path
from typing import List

from core.schemas import CodePatch, RootCauseLink

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MOCK_FILE = PROJECT_ROOT / "test_samples" / "mock_audit_result.json"


def analyze_source_code(
    file_path_or_code: str,
    mock: bool = True,
) -> List[RootCauseLink]:
    """
    Analyzes application source code to locate the root cause of visual/functional defects.
    When mock=True or USE_MOCK is set in environment, extracts deterministic root causes
    from mock_audit_result.json mapped to code locations.
    """
    env_mock = os.getenv("USE_MOCK", "true").strip().lower() in ("true", "1", "yes", "t")
    should_use_mock = mock or env_mock

    if should_use_mock:
        if not DEFAULT_MOCK_FILE.exists():
            raise FileNotFoundError(f"Mock audit file not found at: {DEFAULT_MOCK_FILE}")

        with open(DEFAULT_MOCK_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        raw_root_causes = data.get("root_causes", [])
        validated_causes: List[RootCauseLink] = []

        # Check if file_path_or_code is a valid file path
        candidate_path = Path(file_path_or_code)
        target_name = candidate_path.name if candidate_path.exists() else None

        for item in raw_root_causes:
            cause_data = dict(item)
            if target_name:
                cause_data["target_file"] = target_name
            validated_causes.append(RootCauseLink.model_validate(cause_data))

        return validated_causes

    # Live static analysis / AST / LLM inspection fallback (for future live agents)
    raise NotImplementedError("Live LLM/AST code analysis is not configured yet.")


def generate_code_patch(
    source_code: str,
    root_cause: RootCauseLink,
    mock: bool = True,
) -> CodePatch:
    """
    Generates a deterministic CodePatch remedying the defect identified by root_cause.
    """
    env_mock = os.getenv("USE_MOCK", "true").strip().lower() in ("true", "1", "yes", "t")
    should_use_mock = mock or env_mock

    if should_use_mock:
        # Load default patch from mock_audit_result.json if available
        if DEFAULT_MOCK_FILE.exists():
            with open(DEFAULT_MOCK_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            raw_patches = data.get("patches", [])
            if raw_patches:
                patch_dict = dict(raw_patches[0])
                patch_dict["target_file"] = root_cause.target_file
                patch_dict["target_line"] = root_cause.target_line
                return CodePatch.model_validate(patch_dict)

        # Dynamic fallback matching root cause
        return CodePatch(
            target_file=root_cause.target_file,
            target_line=root_cause.target_line,
            original_snippet="width: 120px;",
            replacement_snippet="width: 100%;",
        )

    raise NotImplementedError("Live LLM patch synthesis is not configured yet.")


def apply_patch_to_code(original_code: str, patch: CodePatch) -> str:
    """
    Applies a CodePatch safely to the provided source code, preserving line structure,
    indentation, and avoiding line duplications.
    """
    lines = original_code.splitlines(keepends=True)
    line_idx = patch.target_line - 1

    if 0 <= line_idx < len(lines):
        target_line = lines[line_idx]

        # Scenario 1: Exact snippet match within the target line
        if patch.original_snippet in target_line:
            lines[line_idx] = target_line.replace(
                patch.original_snippet, patch.replacement_snippet, 1
            )
            return "".join(lines)

        # Scenario 2: Stripped snippet match within the target line
        stripped_orig = patch.original_snippet.strip()
        stripped_repl = patch.replacement_snippet.strip()
        if stripped_orig in target_line:
            lines[line_idx] = target_line.replace(stripped_orig, stripped_repl, 1)
            return "".join(lines)

        # Scenario 3: Complete line replacement preserving target line indentation
        indent = target_line[: len(target_line) - len(target_line.lstrip())]
        newline = "\n" if target_line.endswith("\n") else ""
        lines[line_idx] = f"{indent}{stripped_repl}{newline}"
        return "".join(lines)

    # Fallback: Global snippet substitution if target_line is out of bounds
    if patch.original_snippet in original_code:
        return original_code.replace(patch.original_snippet, patch.replacement_snippet, 1)

    return original_code


def generate_diff_view(original_code: str, patched_code: str) -> str:
    """
    Generates a unified diff using Python standard library difflib, suitable for
    rendering in developer consoles or UI diff viewers.
    """
    orig_lines = original_code.splitlines()
    patched_lines = patched_code.splitlines()

    diff_lines = list(
        difflib.unified_diff(
            orig_lines,
            patched_lines,
            fromfile="original",
            tofile="patched",
            lineterm="",
        )
    )

    return "\n".join(diff_lines)
