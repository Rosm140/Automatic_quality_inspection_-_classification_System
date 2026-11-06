
import cv2
import numpy as np
from pathlib import Path

from src.measurement.dimensional_measurement import measure_od_id

base = Path("data/calibration/test_roi")
roi_path = base / "vertical_pass_001_product_roi.jpg"
edge_path = base / "vertical_pass_001_edges.jpg"

roi = cv2.imread(str(roi_path))
edges = cv2.imread(str(edge_path), cv2.IMREAD_GRAYSCALE)

if roi is None or edges is None:
    raise FileNotFoundError("Could not load ROI or edge image")

# Run the current measurement algorithm.
result = measure_od_id(roi, edges)
print("Current measurement result:")
print(result)

# Reproduce the Hough candidate detection for visualization.
gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 1.2)

circles = cv2.HoughCircles(
    blurred,
    cv2.HOUGH_GRADIENT,
    dp=1.0,
    minDist=10,
    param1=100,
    param2=15,
    minRadius=15,
    maxRadius=150,
)

if circles is None:
    raise RuntimeError("No Hough circles detected")

circles = np.round(circles[0]).astype(int)

# Draw all Hough candidates in yellow.
overlay = roi.copy()

for x, y, radius in circles:
    cv2.circle(overlay, (x, y), radius, (0, 255, 255), 1)
    cv2.circle(overlay, (x, y), 2, (0, 255, 255), -1)

# Draw the final fitted circles.
if result.get("od_radius_px") is not None:
    od_center = (
        round(result["od_center_x"]),
        round(result["od_center_y"]),
    )
    id_center = (
        round(result["id_center_x"]),
        round(result["id_center_y"]),
    )

    cv2.circle(
        overlay,
        od_center,
        round(result["od_radius_px"]),
        (255, 0, 0),
        2,
    )

    cv2.circle(
        overlay,
        id_center,
        round(result["id_radius_px"]),
        (0, 255, 0),
        2,
    )

output_path = base / "hough_candidates_diagnostic.jpg"

if not cv2.imwrite(str(output_path), overlay):
    raise OSError(f"Failed to save diagnostic image: {output_path}")

print(f"\nDiagnostic image saved: {output_path}")
