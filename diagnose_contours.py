
import cv2
import numpy as np
from pathlib import Path

edge_path = Path("data/calibration/test_roi/vertical_pass_001_edges.jpg")

edges = cv2.imread(str(edge_path), cv2.IMREAD_GRAYSCALE)

if edges is None:
    raise FileNotFoundError(edge_path)

contours, _ = cv2.findContours(
    edges,
    cv2.RETR_LIST,
    cv2.CHAIN_APPROX_NONE
)

contours = sorted(
    contours,
    key=cv2.contourArea,
    reverse=True
)

print(f"Total contours: {len(contours)}")
print("\nTop 15 contour measurements:\n")

for index, contour in enumerate(contours[:15]):
    area = cv2.contourArea(contour)
    perimeter = cv2.arcLength(contour, True)

    (cx, cy), radius = cv2.minEnclosingCircle(contour)

    circularity = (
        4 * np.pi * area / (perimeter * perimeter)
        if perimeter > 0 else 0
    )

    print(
        f"{index}: "
        f"Area={area:.2f}, "
        f"Diameter={2 * radius:.2f}px, "
        f"Center=({cx:.2f}, {cy:.2f}), "
        f"Circularity={circularity:.3f}, "
        f"Points={len(contour)}"
    )
