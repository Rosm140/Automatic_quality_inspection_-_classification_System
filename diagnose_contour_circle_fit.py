import cv2
import numpy as np
from pathlib import Path

path = Path("data/calibration/test_roi/vertical_pass_001_edges.jpg")
edges = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)

contours, _ = cv2.findContours(
    edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE
)
contours = sorted(contours, key=cv2.contourArea, reverse=True)

for i in [0, 1]:
    points = contours[i].reshape(-1, 2).astype(np.float64)
    x, y = points[:, 0], points[:, 1]

    A = np.column_stack((2*x, 2*y, np.ones(len(points))))
    b = x*x + y*y
    cx, cy, c = np.linalg.lstsq(A, b, rcond=None)[0]
    radius = np.sqrt(c + cx*cx + cy*cy)

    residuals = np.abs(np.sqrt((x-cx)**2 + (y-cy)**2) - radius)

    print(
        f"Contour {i}: diameter={2*radius:.2f}px, "
        f"center=({cx:.2f},{cy:.2f}), "
        f"mean radial error={residuals.mean():.2f}px"
    )
