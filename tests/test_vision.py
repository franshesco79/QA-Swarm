"""
Unit tests for QA-Swarm core/vision.py module.
Verifies coordinate normalization, bounding box rendering, and mock UI inspection.
"""

import os
from pathlib import Path
from PIL import Image
import pytest

from core.schemas import VisualDefect
from core.vision import (
    normalize_coordinates,
    draw_bounding_boxes,
    inspect_ui_elements,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SAMPLE_UI_PATH = PROJECT_ROOT / "test_samples" / "sample_ui.png"


def test_normalize_coordinates_clamping():
    """
    Validates that out-of-range coordinates (negative or exceeding dimensions/1.0)
    clamp safely to the image boundaries [0, width] and [0, height] without IndexError.
    """
    img_width, img_height = 800, 600

    # Test 1: Negative and overflowing absolute pixel coordinates
    out_of_bounds_abs = [-50.0, -100.0, 950.0, 1200.0]
    x0, y0, x1, y1 = normalize_coordinates(out_of_bounds_abs, img_width, img_height)
    assert (x0, y0, x1, y1) == (0, 0, 800, 600)
    assert 0 <= x0 <= x1 <= img_width
    assert 0 <= y0 <= y1 <= img_height

    # Test 2: Negative and overflowing relative coordinates (> 1.0)
    out_of_bounds_rel = [-0.25, -0.15, 1.35, 1.40]
    rx0, ry0, rx1, ry1 = normalize_coordinates(out_of_bounds_rel, img_width, img_height)
    assert (rx0, ry0, rx1, ry1) == (0, 0, 800, 600)

    # Test 3: Standard in-range relative coordinates
    in_range_rel = [0.1, 0.2, 0.5, 0.6]  # ymin, xmin, ymax, xmax
    ix0, iy0, ix1, iy1 = normalize_coordinates(in_range_rel, img_width, img_height)
    assert (ix0, iy0, ix1, iy1) == (160, 60, 480, 300)

    # Test 4: Standard in-range absolute coordinates
    in_range_abs = [420.0, 150.0, 480.0, 310.0]
    ax0, ay0, ax1, ay1 = normalize_coordinates(in_range_abs, img_width, img_height)
    assert (ax0, ay0, ax1, ay1) == (150, 420, 310, 480)


def test_draw_bounding_boxes_creates_file():
    """
    Validates that draw_bounding_boxes generates a non-empty image file with valid dimensions.
    """
    assert SAMPLE_UI_PATH.exists(), f"Sample UI image must exist at {SAMPLE_UI_PATH}"

    defects = [
        VisualDefect(
            element_name="btn_purchase",
            bbox=[420.0, 150.0, 480.0, 310.0],
            defect_type="LAYOUT_OVERFLOW",
            severity="CRITICAL",
        )
    ]

    target_output = PROJECT_ROOT / "test_samples" / "annotated_ui.png"
    if target_output.exists():
        target_output.unlink()

    result_path = draw_bounding_boxes(
        image_path=str(SAMPLE_UI_PATH),
        defects=defects,
        output_path=str(target_output),
    )

    assert os.path.exists(result_path)
    assert os.path.isfile(result_path)
    assert os.path.getsize(result_path) > 0

    # Ensure output image is valid and preserves resolution
    with Image.open(result_path) as img:
        assert img.size in ((1280, 800), (800, 600))
        assert img.format == "PNG"


def test_inspect_ui_elements_mock():
    """
    Validates that inspect_ui_elements with mock=True returns valid VisualDefect instances.
    """
    assert SAMPLE_UI_PATH.exists(), f"Sample UI image must exist at {SAMPLE_UI_PATH}"

    defects = inspect_ui_elements(image_path=str(SAMPLE_UI_PATH), mock=True)

    assert isinstance(defects, list)
    assert len(defects) >= 1

    first_defect = defects[0]
    assert isinstance(first_defect, VisualDefect)
    assert first_defect.element_name == "btn_purchase"
    assert first_defect.defect_type == "LAYOUT_OVERFLOW"
    assert first_defect.severity == "CRITICAL"
    assert len(first_defect.bbox) == 4
    assert first_defect.bbox == [420.0, 150.0, 480.0, 310.0]
