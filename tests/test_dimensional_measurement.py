
import numpy as np

from src.measurement.dimensional_measurement import (
    fit_circle_robust,
    measure_od_id,
    check_measurement_quality,
)
def test_fit_circle_recovers_known_circle():
    angles = np.linspace(0, 2 * np.pi, 100, endpoint=False)

    points = np.column_stack(
        (
            50 + 20 * np.cos(angles),
            40 + 20 * np.sin(angles),
        )
    )

    result = fit_circle_robust(points)

    assert result is not None
    assert abs(result["cx"] - 50) < 0.01
    assert abs(result["cy"] - 40) < 0.01
    assert abs(result["radius"] - 20) < 0.01
    assert result["fit_error_px"] < 0.01


def test_measure_od_id_rejects_empty_roi():
    import pytest

    from src.measurement.dimensional_measurement import measure_od_id

    with pytest.raises(ValueError, match="Product ROI is empty"):
        measure_od_id(np.array([]), np.array([]))



def test_fit_circle_handles_small_noise():
    rng = np.random.default_rng(42)
    angles = np.linspace(0, 2 * np.pi, 200, endpoint=False)

    points = np.column_stack(
        (
            50 + 20 * np.cos(angles),
            40 + 20 * np.sin(angles),
        )
    )
    points += rng.normal(0, 0.3, points.shape)

    result = fit_circle_robust(points)

    assert result is not None
    assert abs(result["cx"] - 50) < 0.1
    assert abs(result["cy"] - 40) < 0.1
    assert abs(result["radius"] - 20) < 0.1
    assert result["fit_error_px"] < 0.5


from pathlib import Path

import cv2


def test_real_roi_returns_unvalidated_pixel_estimates():
    project_root = Path(__file__).resolve().parents[1]
    roi_path = (
        project_root
        / "data"
        / "calibration"
        / "test_roi"
        / "vertical_pass_001_product_roi.jpg"
    )
    edge_path = (
        project_root
        / "data"
        / "calibration"
        / "test_roi"
        / "vertical_pass_001_edges.jpg"
    )

    roi = cv2.imread(str(roi_path))
    edges = cv2.imread(str(edge_path), cv2.IMREAD_GRAYSCALE)

    assert roi is not None, f"Missing ROI image: {roi_path}"
    assert edges is not None, f"Missing edge image: {edge_path}"

    result = measure_od_id(roi, edges)

    assert result["status"] == "estimated"
    assert result["od_px"] > result["id_px"] > 0
    assert result["units"] == "pixels"
    assert result["validated"] is False



def test_measurement_quality_accepts_consistent_geometry():
    result = check_measurement_quality(
        id_fit_error_px=1.0,
        od_fit_error_px=1.2,
        center_difference_px=0.5,
        id_od_ratio=0.76,
    )

    assert result["passed"] is True
    assert result["failure_reasons"] == []


def test_measurement_quality_rejects_excessive_fit_error():
    result = check_measurement_quality(
        id_fit_error_px=3.5,
        od_fit_error_px=1.2,
        center_difference_px=0.5,
        id_od_ratio=0.76,
    )

    assert result["passed"] is False
    assert "id_fit_error_ok" in result["failure_reasons"]
