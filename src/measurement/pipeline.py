"""Minimal saved-image dimensional inspection pipeline."""

import argparse
import json
from pathlib import Path

import cv2
import numpy as np

from src.measurement.dimensional_measurement import measure_od_id
from src.measurement.undistortion import load_calibration, undistort_image


def inspect_image(image_path: str | Path) -> dict:
    """Inspect a saved image and return a JSON-compatible summary."""
    path = Path(image_path)
    result = {
        "image_filename": path.name,
        "processing_status": "failed",
        "image_dimensions": None,
        "undistortion_status": "not_attempted",
        "od": None,
        "id": None,
        "measurement_units": "px",
        "validation_status": "NOT_EVALUATED",
        "acceptance_criteria": "UNDEFINED",
        "defect_detection_status": "NOT_IMPLEMENTED",
        "errors": [],
        "warnings": [],
    }

    if not path.is_file():
        result["errors"].append(f"Image file does not exist: {path}")
        return result

    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None or image.size == 0:
        result["errors"].append(f"OpenCV could not read image: {path}")
        return result

    height, width = image.shape[:2]
    result["image_dimensions"] = {"width": int(width), "height": int(height)}

    try:
        _, _, metadata = load_calibration()
        resolution = metadata["resolution"]
        expected_size = (int(resolution["width"]), int(resolution["height"]))
    except (FileNotFoundError, KeyError, TypeError, ValueError, OSError) as exc:
        result["undistortion_status"] = "skipped_calibration_unavailable"
        result["warnings"].append(f"Calibration unavailable; image left unchanged: {exc}")
    else:
        actual_size = (width, height)
        if actual_size == expected_size:
            try:
                image = undistort_image(image)
                result["undistortion_status"] = "applied"
            except (FileNotFoundError, KeyError, TypeError, ValueError, OSError) as exc:
                result["undistortion_status"] = "failed"
                result["warnings"].append(f"Undistortion failed; using original image: {exc}")
        else:
            result["undistortion_status"] = "skipped_resolution_mismatch"
            result["warnings"].append(
                f"Image resolution {actual_size} does not match calibration "
                f"{expected_size}; undistortion skipped."
            )

    try:
        edges = cv2.Canny(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), 50, 150)
        measurement = measure_od_id(image, edges)
    except Exception as exc:
        result["errors"].append(f"Dimensional measurement failed: {exc}")
        return result

    if not isinstance(measurement, dict):
        result["errors"].append("Dimensional measurement returned an invalid result (expected an object).")
        return result

    od = measurement.get("od_px")
    inner_diameter = measurement.get("id_px")
    if not _valid_diameter(od) or not _valid_diameter(inner_diameter):
        reason = measurement.get("reason") or measurement.get("status") or "missing or invalid OD/ID values"
        result["errors"].append(f"Dimensional measurement failed: {reason}")
        return result

    result["od"] = float(od)
    result["id"] = float(inner_diameter)
    result["measurement_units"] = "px"
    result["processing_status"] = "completed"
    result["warnings"].append("Measurements are pixel estimates; no validated physical scale or acceptance criteria are configured.")
    return result


def _valid_diameter(value) -> bool:
    try:
        return np.isfinite(float(value)) and float(value) > 0
    except (TypeError, ValueError):
        return False


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Inspect a saved product image.")
    parser.add_argument("image_path", help="Path to a saved image")
    args = parser.parse_args(argv)
    result = inspect_image(args.image_path)
    print(json.dumps(result, indent=2))
    return 0 if result["processing_status"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
