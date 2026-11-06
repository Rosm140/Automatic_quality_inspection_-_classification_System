import cv2
import numpy as np
from pathlib import Path

path = Path("data/calibration/test_roi/vertical_pass_001_product_roi.jpg")
image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)

if image is None:
    raise FileNotFoundError(path)

cx, cy = 149.18, 150.49
angles = np.linspace(0, 2 * np.pi, 360, endpoint=False)

print("Radius(px) | Mean intensity | Mean gradient")

for radius in np.arange(15, 31, 1):
    values = []
    gradients = []

    for angle in angles:
        x = int(round(cx + radius * np.cos(angle)))
        y = int(round(cy + radius * np.sin(angle)))

        if 1 <= x < image.shape[1] - 1 and 1 <= y < image.shape[0] - 1:
            values.append(float(image[y, x]))
            gx = float(image[y, x + 1]) - float(image[y, x - 1])
            gy = float(image[y + 1, x]) - float(image[y - 1, x])
            gradients.append(np.hypot(gx, gy))

    print(
        f"{radius:9.1f} | "
        f"{np.mean(values):14.2f} | "
        f"{np.mean(gradients):13.2f}"
    )
