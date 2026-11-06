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

contours = sorted(contours, key=cv2.contourArea, reverse=True)

# Show only the two largest contours
image = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

for index, contour in enumerate(contours[:2]):
    color = (0, 255, 255) if index == 0 else (255, 0, 255)
    cv2.drawContours(image, [contour], -1, color, 2)

    (cx, cy), radius = cv2.minEnclosingCircle(contour)
    cv2.circle(
        image,
        (int(round(cx)), int(round(cy))),
        int(round(radius)),
        color,
        1
    )

output_path = Path("data/calibration/test_roi/top_contours_visual.jpg")
cv2.imwrite(str(output_path), image)

print(f"Saved visualization: {output_path}")