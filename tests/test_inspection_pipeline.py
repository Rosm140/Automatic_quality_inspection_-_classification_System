import cv2
import numpy as np

from src.measurement import pipeline


def _image(path, size=(240, 240)):
    image = np.zeros((size[1], size[0], 3), dtype=np.uint8)
    cv2.circle(image, (size[0] // 2, size[1] // 2), 70, (255, 255, 255), 3)
    cv2.circle(image, (size[0] // 2, size[1] // 2), 45, (255, 255, 255), 3)
    assert cv2.imwrite(str(path), image)
    return image


def test_valid_saved_image_returns_pixel_result_and_undefined_validation(tmp_path, monkeypatch):
    image_path = tmp_path / "product.png"
    _image(image_path)
    monkeypatch.setattr(pipeline, "load_calibration", lambda: (_ for _ in ()).throw(FileNotFoundError("test")))
    monkeypatch.setattr(pipeline, "measure_od_id", lambda roi, edges: {
        "status": "estimated", "od_px": 140.0, "id_px": 90.0,
    })

    result = pipeline.inspect_image(image_path)

    assert result["processing_status"] == "completed"
    assert result["image_filename"] == "product.png"
    assert result["image_dimensions"] == {"width": 240, "height": 240}
    assert result["od"] == 140.0 and result["id"] == 90.0
    assert result["measurement_units"] == "px"
    assert result["validation_status"] == "NOT_EVALUATED"
    assert result["acceptance_criteria"] == "UNDEFINED"
    assert result["defect_detection_status"] == "NOT_IMPLEMENTED"


def test_nonexistent_image_returns_failure(tmp_path):
    result = pipeline.inspect_image(tmp_path / "missing.png")
    assert result["processing_status"] == "failed"
    assert result["errors"]


def test_unreadable_image_returns_failure(tmp_path):
    image_path = tmp_path / "unreadable.png"
    image_path.write_text("not an image", encoding="utf-8")
    result = pipeline.inspect_image(image_path)
    assert result["processing_status"] == "failed"
    assert "could not read" in result["errors"][0]


def test_missing_or_invalid_measurement_is_failure(tmp_path, monkeypatch):
    image_path = tmp_path / "product.png"
    _image(image_path)
    monkeypatch.setattr(pipeline, "load_calibration", lambda: (_ for _ in ()).throw(FileNotFoundError("test")))
    monkeypatch.setattr(pipeline, "measure_od_id", lambda roi, edges: {"status": "no_valid_circle_pair"})

    result = pipeline.inspect_image(image_path)

    assert result["processing_status"] == "failed"
    assert result["od"] is None and result["id"] is None
    assert result["errors"]


def test_acceptance_criteria_remain_undefined_when_measurement_succeeds(tmp_path, monkeypatch):
    image_path = tmp_path / "product.png"
    _image(image_path)
    monkeypatch.setattr(pipeline, "load_calibration", lambda: (_ for _ in ()).throw(FileNotFoundError("test")))
    monkeypatch.setattr(pipeline, "measure_od_id", lambda roi, edges: {"status": "estimated", "od_px": 120, "id_px": 80})

    result = pipeline.inspect_image(image_path)

    assert result["processing_status"] == "completed"
    assert result["validation_status"] == "NOT_EVALUATED"
    assert result["acceptance_criteria"] == "UNDEFINED"


def test_1920x1080_image_skips_unconfigured_calibration(tmp_path, monkeypatch):
    image_path = tmp_path / "high-resolution.png"
    image = _image(image_path, size=(1920, 1080))
    monkeypatch.setattr(
        pipeline,
        "load_calibration",
        lambda: (None, None, {"resolution": {"width": 1280, "height": 720}}),
    )

    def unexpected_undistortion(_image):
        raise AssertionError("Unconfigured resolution must not be undistorted")

    monkeypatch.setattr(pipeline, "undistort_image", unexpected_undistortion)
    measured_shapes = []

    def measure(roi, edges):
        measured_shapes.append(roi.shape)
        return {"status": "estimated", "od_px": 140.0, "id_px": 90.0}

    monkeypatch.setattr(pipeline, "measure_od_id", measure)

    result = pipeline.inspect_image(image_path)

    assert result["image_dimensions"] == {"width": 1920, "height": 1080}
    assert result["undistortion_status"] == "skipped_resolution_mismatch"
    assert result["processing_status"] == "completed"
    assert measured_shapes == [image.shape]
    assert "(1920, 1080)" in result["warnings"][0]
