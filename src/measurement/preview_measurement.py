
import json
from pathlib import Path

import cv2

from src.measurement.dimensional_measurement import measure_od_id

base = Path("data/calibration/test_roi")
roi_path = base / "vertical_pass_001_product_roi.jpg"
edge_path = base / "vertical_pass_001_edges.jpg"

roi = cv2.imread(str(roi_path))
edges = cv2.imread(str(edge_path), cv2.IMREAD_GRAYSCALE)

if roi is None or edges is None:
    raise FileNotFoundError(
        f"Could not load ROI or edge image: {roi_path}, {edge_path}"
    )

result = measure_od_id(roi, edges)
print(json.dumps(result, indent=2))

if result.get("od_px") is None or result.get("id_px") is None:
    raise RuntimeError(
        f"Measurement failed: {result.get('status')} - "
        f"{result.get('reason', result.get('failure_reasons', 'Unknown reason'))}"
    )

overlay = roi.copy()

# Use the actual fitted centers and radii returned by the measurement code.
for center_x_key, center_y_key, radius_key, color, label, diameter_key in [
    (
        "od_center_x", "od_center_y", "od_radius_px",
        (255, 0, 0), "OD", "od_px"
    ),
    (
        "id_center_x", "id_center_y", "id_radius_px",
        (0, 255, 0), "ID", "id_px"
    ),
]:
    center_x = result.get(center_x_key)
    center_y = result.get(center_y_key)
    radius = result.get(radius_key)

    if center_x is not None and center_y is not None and radius is not None:
        center = (round(center_x), round(center_y))
        cv2.circle(overlay, center, round(radius), color, 2)
        cv2.circle(overlay, center, 3, color, -1)

        cv2.putText(
            overlay,
            f"{label}: {result[diameter_key]:.2f} px",
            (10, 25 if label == "OD" else 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            color,
            2,
            cv2.LINE_AA,
        )

status = result.get("status", "unknown")
center_diff = result.get("center_difference_px")

cv2.putText(
    overlay,
    f"Status: {status}",
    (10, 75),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.5,
    (255, 255, 255),
    1,
    cv2.LINE_AA,
)

if center_diff is not None:
    cv2.putText(
        overlay,
        f"Center difference: {center_diff:.2f} px",
        (10, 100),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 255, 255),
        1,
        cv2.LINE_AA,
    )

output = base / "measurement_overlay_preview.jpg"

if not cv2.imwrite(str(output), overlay):
    raise OSError(f"Failed to save overlay: {output}")

print(f"\nPreview saved: {output}")
print(f"Measurement status: {status}")
print("Units: pixels; physical accuracy not validated.")
