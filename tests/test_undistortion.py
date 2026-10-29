from pathlib import Path

import cv2
import numpy as np
import pytest

import src.measurement.undistortion as undistortion
from src.measurement.undistortion import (
    load_calibration,
    undistort_file,
    undistort_image,
)
from src.utils.config_loader import load_config
from src.utils.constants import PROJECT_ROOT


def test_calibration_config_paths_exist_and_match_metadata():
    calibration = load_config("calibration.yaml")["calibration"]
    files = calibration["files"]

    for key in ("parameters", "camera_matrix", "distortion_coefficients"):
        assert (PROJECT_ROOT / files[key]).is_file()

    _, _, metadata = load_calibration()
    assert calibration["resolution"] == metadata["resolution"]
    assert metadata["resolution"] == {"width": 1280, "height": 720}


def test_missing_calibration_file_raises(tmp_path, monkeypatch):
    monkeypatch.setattr(undistortion, "PROJECT_ROOT", tmp_path)

    with pytest.raises(FileNotFoundError, match="camera matrix"):
        load_calibration()


def test_saved_image_can_be_undistorted_to_temporary_output(tmp_path):
    image_path = (
        PROJECT_ROOT
        / "data"
        / "calibration"
        / "calibration_001_undistorted.jpg"
    )
    output_path = tmp_path / "undistorted-preview.jpg"

    image = cv2.imread(str(image_path))
    assert image is not None, f"Could not read saved image: {image_path}"
    assert image.shape[:2] == (720, 1280)

    result_path = undistort_file(str(image_path), str(output_path))

    assert result_path == output_path
    assert result_path.is_file()
    result = cv2.imread(str(result_path))
    assert result is not None
    assert result.shape == image.shape


@pytest.mark.parametrize("size", [(1920, 1080), (300, 300)])
def test_undistort_image_rejects_unconfigured_resolution(size):
    image = np.zeros((size[1], size[0], 3), dtype=np.uint8)

    with pytest.raises(
        ValueError,
        match=rf"Image resolution \({size[0]}, {size[1]}\) does not match calibration "
        r"\(1280, 720\); no calibration transform is configured",
    ):
        undistort_image(image)
