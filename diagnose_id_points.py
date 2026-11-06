
import cv2
import numpy as np
from pathlib import Path

base = Path("data/calibration/test_roi")
roi = cv2.imread(str(base / "vertical_pass_001_product_roi.jpg"))
edges = cv2.imread(
    str(base / "vertical_pass_001_edges.jpg"),
    cv2.IMREAD_GRAYSCALE,
)

if roi is None or edges is None:
    raise FileNotFoundError("Could not load ROI or edge image")

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
ys, xs = np.where(edges > 0)
edge_points = np.column_stack((xs, ys))

expected_ratio = 0.380 / 0.500
pairs = []

for i in range(len(circles)):
    x1, y1, r1 = circles[i]

    for j in range(i + 1, len(circles)):
        x2, y2, r2 = circles[j]

        inner_radius, outer_radius = sorted((r1, r2))

        if inner_radius <= 0 or outer_radius <= inner_radius:
            continue

        ratio = inner_radius / outer_radius
        center_distance = float(np.hypot(x1 - x2, y1 - y2))

        if not 0.55 <= ratio <= 0.90 or center_distance > 18:
            continue

        score = (
            abs(ratio - expected_ratio) * 2
            + center_distance / 18
        )

        pairs.append(
            (
                score,
                (x1 + x2) / 2,
                (y1 + y2) / 2,
                inner_radius,
                outer_radius,
            )
        )

if not pairs:
    raise RuntimeError("No valid circle pair found")

score, cx, cy, inner_radius, outer_radius = min(
    pairs, key=lambda pair: pair[0]
)

radial_distances = np.hypot(
    edge_points[:, 0] - cx,
    edge_points[:, 1] - cy,
)

id_points = edge_points[
    np.abs(radial_distances - inner_radius) <= 4.0
]

print(f"Selected candidate ID radius: {inner_radius} px")
print(f"Selected candidate OD radius: {outer_radius} px")
print(f"Selected ID edge points: {len(id_points)}")

# Highlight selected ID points in magenta.
overlay = roi.copy()

overlay[id_points[:, 1], id_points[:, 0]] = (255, 0, 255)

# Draw selected Hough candidate circles.
cv2.circle(
    overlay,
    (round(cx), round(cy)),
    int(inner_radius),
    (0, 255, 255),
    1,
)

cv2.circle(
    overlay,
    (round(cx), round(cy)),
    int(outer_radius),
    (255, 255, 0),
    1,
)

output_path = base / "selected_id_points.jpg"

if not cv2.imwrite(str(output_path), overlay):
    raise OSError(f"Failed to save: {output_path}")

print(f"Diagnostic image saved: {output_path}")
