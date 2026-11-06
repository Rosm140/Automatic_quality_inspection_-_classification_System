import cv2
from pathlib import Path

roi_path = Path("data/calibration/test_roi/vertical_pass_001_product_roi.jpg")
image = cv2.imread(str(roi_path))

if image is None:
    raise FileNotFoundError(roi_path)

# Circle fits from our contour diagnostic
outer_center = (148.93, 149.20)
outer_radius = 69.16 / 2

inner_center = (149.18, 150.49)
inner_radius = 42.93 / 2

# Outer contour: yellow
cv2.circle(
    image,
    tuple(round(v) for v in outer_center),
    round(outer_radius),
    (0, 255, 255),
    2
)

# Inner contour: magenta
cv2.circle(
    image,
    tuple(round(v) for v in inner_center),
    round(inner_radius),
    (255, 0, 255),
    2
)

output_path = Path("data/calibration/test_roi/contour_fits_on_roi.jpg")
cv2.imwrite(str(output_path), image)

print(f"Saved overlay: {output_path}")
