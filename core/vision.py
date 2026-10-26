"""
Vision module for QA-Swarm.
Provides coordinate normalization, spatial bounding box annotations,
and UI defect inspection.
"""

import json
import os
from pathlib import Path
from typing import List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont
from core.schemas import VisualDefect

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MOCK_FILE = PROJECT_ROOT / "test_samples" / "mock_audit_result.json"
DEFAULT_ANNOTATED_OUTPUT = PROJECT_ROOT / "test_samples" / "annotated_ui.png"


def normalize_coordinates(
    bbox: List[float], img_width: int, img_height: int
) -> Tuple[int, int, int, int]:
    """
    Converts bounding box coordinates [ymin, xmin, ymax, xmax] (whether relative [0.0 - 1.0]
    or absolute pixels) into clamped integer pixel coordinates (xmin, ymin, xmax, ymax)
    strictly within the image dimensions.

    Returns:
        tuple[int, int, int, int]: (xmin, ymin, xmax, ymax) ready for PIL drawing operations.
    """
    if len(bbox) != 4:
        raise ValueError(f"Expected 4 coordinates for bbox [ymin, xmin, ymax, xmax], got {len(bbox)}")

    ymin, xmin, ymax, xmax = bbox

    # Detect if coordinates are relative/normalized (e.g. 0.0 to 1.0 or slight overflow range)
    # If all absolute coordinates are within <= 2.0 and image dimensions are substantial (> 10)
    is_relative = (
        max(abs(ymin), abs(xmin), abs(ymax), abs(xmax)) <= 2.0
        and img_width > 10
        and img_height > 10
    )

    if is_relative:
        ymin = ymin * img_height
        xmin = xmin * img_width
        ymax = ymax * img_height
        xmax = xmax * img_width

    # Clamp safely to image boundaries
    x0 = max(0, min(img_width, int(round(xmin))))
    y0 = max(0, min(img_height, int(round(ymin))))
    x1 = max(0, min(img_width, int(round(xmax))))
    y1 = max(0, min(img_height, int(round(ymax))))

    # Ensure coordinates are properly ordered (x0 <= x1 and y0 <= y1)
    if x0 > x1:
        x0, x1 = x1, x0
    if y0 > y1:
        y0, y1 = y1, y0

    return (x0, y0, x1, y1)


def draw_bounding_boxes(
    image_path: str,
    defects: List[VisualDefect],
    output_path: Optional[str] = None,
) -> str:
    """
    Opens an image, renders semi-transparent fill and solid red bounding boxes (#FF3B30, 3px)
    for each visual defect, adds a human-readable badge with defect_type and severity,
    and writes the annotated image to output_path.

    Returns:
        str: Absolute path of the generated annotated image.
    """
    resolved_img_path = Path(image_path).resolve()
    if not resolved_img_path.exists():
        raise FileNotFoundError(f"Source image not found: {resolved_img_path}")

    target_output = (
        Path(output_path).resolve()
        if output_path
        else DEFAULT_ANNOTATED_OUTPUT
    )
    target_output.parent.mkdir(parents=True, exist_ok=True)

    base_image = Image.open(resolved_img_path).convert("RGBA")
    img_width, img_height = base_image.size

    # Create overlay for alpha blending (translucent fills)
    overlay = Image.new("RGBA", (img_width, img_height), (0, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)

    # Use default bitmap font
    font = ImageFont.load_default()

    RED_BORDER = (255, 59, 48, 255)       # #FF3B30 opaque
    RED_TRANSLUCENT = (255, 59, 48, 48)   # #FF3B30 ~19% opacity
    BADGE_BG = (255, 59, 48, 230)         # High opacity badge
    TEXT_COLOR = (255, 255, 255, 255)     # Crisp white text

    for defect in defects:
        x0, y0, x1, y1 = normalize_coordinates(defect.bbox, img_width, img_height)

        # 1. Semi-transparent defect region fill
        draw_overlay.rectangle([x0, y0, x1, y1], fill=RED_TRANSLUCENT)

        # 2. Solid 3px red outline
        draw_overlay.rectangle([x0, y0, x1, y1], outline=RED_BORDER, width=3)

        # 3. Label badge
        label_text = f"{defect.defect_type} [{defect.severity}]"
        
        # Calculate text bounding box
        try:
            bbox_text = draw_overlay.textbbox((0, 0), label_text, font=font)
            text_w = bbox_text[2] - bbox_text[0]
            text_h = bbox_text[3] - bbox_text[1]
        except Exception:
            text_w = len(label_text) * 7
            text_h = 12

        pad_x, pad_y = 6, 4
        badge_w = text_w + (pad_x * 2)
        badge_h = text_h + (pad_y * 2)

        # Place badge directly above bbox if space permits, else inside top-left
        badge_y0 = y0 - badge_h if y0 >= badge_h else y0
        badge_x0 = max(0, min(img_width - badge_w, x0))
        badge_x1 = badge_x0 + badge_w
        badge_y1 = badge_y0 + badge_h

        draw_overlay.rectangle([badge_x0, badge_y0, badge_x1, badge_y1], fill=BADGE_BG)
        draw_overlay.text(
            (badge_x0 + pad_x, badge_y0 + pad_y),
            label_text,
            fill=TEXT_COLOR,
            font=font,
        )

    # Composite overlay on top of original image
    annotated = Image.alpha_composite(base_image, overlay).convert("RGB")
    annotated.save(target_output, "PNG")

    return str(target_output.resolve())


def inspect_ui_elements(image_path: str, mock: bool = True) -> List[VisualDefect]:
    """
    Inspects UI elements in the target image. When mock=True or USE_MOCK environment variable
    is True, returns deterministic defects from mock_audit_result.json scaled to image dimensions.
    """
    env_mock = os.getenv("USE_MOCK", "true").strip().lower() in ("true", "1", "yes", "t")
    should_use_mock = mock or env_mock

    resolved_img_path = Path(image_path).resolve()
    if not resolved_img_path.exists():
        raise FileNotFoundError(f"Target image for inspection not found: {resolved_img_path}")

    with Image.open(resolved_img_path) as img:
        img_width, img_height = img.size

    if should_use_mock:
        if not DEFAULT_MOCK_FILE.exists():
            raise FileNotFoundError(f"Mock file not found at: {DEFAULT_MOCK_FILE}")

        with open(DEFAULT_MOCK_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        raw_defects = data.get("defects", [])
        validated_defects: List[VisualDefect] = []

        # Standard reference resolution of mock dataset is 800x600
        ref_width, ref_height = 800.0, 600.0
        scale_x = img_width / ref_width
        scale_y = img_height / ref_height

        for item in raw_defects:
            original_bbox = item.get("bbox", [0.0, 0.0, 0.0, 0.0])
            ymin, xmin, ymax, xmax = original_bbox

            # If image matches reference, keep exact bbox; otherwise scale proportionally
            if (img_width, img_height) == (800, 600):
                scaled_bbox = [float(ymin), float(xmin), float(ymax), float(xmax)]
            else:
                scaled_bbox = [
                    round(ymin * scale_y, 2),
                    round(xmin * scale_x, 2),
                    round(ymax * scale_y, 2),
                    round(xmax * scale_x, 2),
                ]

            defect_copy = dict(item)
            defect_copy["bbox"] = scaled_bbox
            validated_defects.append(VisualDefect.model_validate(defect_copy))

        return validated_defects

    # Live inference fallback (for future live SAM 3.1 endpoint)
    raise NotImplementedError("Live vision model inference endpoint not configured yet.")
