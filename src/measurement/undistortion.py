from pathlib import Path

import cv2
import numpy as np

from src.utils.config_loader import load_config
from src.utils.constants import PROJECT_ROOT


def load_calibration():
    """Load camera calibration parameters and metadata."""
    import json

    calibration = load_config("calibration.yaml")["calibration"]
    files = calibration["files"]
    required_files = {
        "camera matrix": PROJECT_ROOT / files["camera_matrix"],
        "distortion coefficients": PROJECT_ROOT / files["distortion_coefficients"],
        "calibration metadata": PROJECT_ROOT / files["parameters"],
    }

    for label, path in required_files.items():
        if not path.is_file():
            raise FileNotFoundError(
                f"Calibration {label} file not found: {path}"
            )

    camera_matrix = np.load(required_files["camera matrix"])
    distortion = np.load(required_files["distortion coefficients"])

    with required_files["calibration metadata"].open(
        "r", encoding="utf-8"
    ) as file:
        metadata = json.load(file)

    if camera_matrix.shape != (3, 3):
        raise ValueError(
            f"Expected a 3x3 camera matrix, got {camera_matrix.shape}"
        )

    if distortion.size < 4:
        raise ValueError("Distortion coefficients are incomplete")

    configured_resolution = calibration["resolution"]
    metadata_resolution = metadata["resolution"]
    configured_size = (
        int(configured_resolution["width"]),
        int(configured_resolution["height"]),
    )
    metadata_size = (
        int(metadata_resolution["width"]),
        int(metadata_resolution["height"]),
    )
    if configured_size != metadata_size:
        raise ValueError(
            "Calibration configuration resolution "
            f"{configured_size} does not match calibration metadata "
            f"{metadata_size}"
        )

    return camera_matrix, distortion, metadata


def undistort_image(image: np.ndarray) -> np.ndarray:
    """Undistort an image using calibration for its exact resolution."""
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")

    camera_matrix, distortion, metadata = load_calibration()
    expected = metadata["resolution"]
    expected_size = (int(expected["width"]), int(expected["height"]))
    actual_size = (image.shape[1], image.shape[0])

    if actual_size != expected_size:
        raise ValueError(
            f"Image resolution {actual_size} does not match calibration "
            f"{expected_size}; no calibration transform is configured for "
            "this resolution. Capture at the calibrated resolution."
        )

    return cv2.undistort(image, camera_matrix, distortion)


def undistort_file(input_path: str, output_path: str) -> Path:
    """Undistort an image file and save the result."""
    image = cv2.imread(input_path)
    if image is None:
        raise FileNotFoundError(f"Could not read image: {input_path}")

    result = undistort_image(image)
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    if not cv2.imwrite(str(destination), result):
        raise OSError(f"Could not save undistorted image: {destination}")

    return destination
