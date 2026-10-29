
import cv2
import numpy as np


# Provisional geometric screening limits.
# These are not validated industrial acceptance limits.
MAX_FIT_ERROR_PX = 2.5
MAX_CENTER_DIFFERENCE_PX = 3.0
MIN_ID_OD_RATIO = 0.55
MAX_ID_OD_RATIO = 0.90

def check_measurement_quality(
    id_fit_error_px,
    od_fit_error_px,
    center_difference_px,
    id_od_ratio,
):
    """Screen circle measurements for geometric consistency."""
    checks = {
        "id_fit_error_ok": (
            np.isfinite(id_fit_error_px)
            and 0 <= id_fit_error_px <= MAX_FIT_ERROR_PX
        ),
        "od_fit_error_ok": (
            np.isfinite(od_fit_error_px)
            and 0 <= od_fit_error_px <= MAX_FIT_ERROR_PX
        ),
        "center_alignment_ok": (
            np.isfinite(center_difference_px)
            and 0 <= center_difference_px <= MAX_CENTER_DIFFERENCE_PX
        ),
        "id_od_ratio_ok": (
            np.isfinite(id_od_ratio)
            and MIN_ID_OD_RATIO <= id_od_ratio <= MAX_ID_OD_RATIO
        ),
    }

    return {
        "passed": all(checks.values()),
        "checks": checks,
        "failure_reasons": [
            name for name, passed in checks.items() if not passed
        ],
    }


def fit_circle_robust(points):
    """Fit a circle and reject points with large radial errors."""
    points = np.asarray(points, dtype=np.float64)

    if points.ndim != 2 or points.shape[1] != 2 or len(points) < 20:
        return None

    def fit(x, y):
        matrix = np.column_stack((x, y, np.ones_like(x)))
        target = -(x * x + y * y)

        try:
            d, e, f = np.linalg.lstsq(
                matrix, target, rcond=None
            )[0]
        except np.linalg.LinAlgError:
            return None

        cx, cy = -d / 2.0, -e / 2.0
        radius_squared = cx * cx + cy * cy - f

        if not np.isfinite(radius_squared) or radius_squared <= 0:
            return None

        return cx, cy, float(np.sqrt(radius_squared))

    x, y = points[:, 0], points[:, 1]
    initial = fit(x, y)

    if initial is None:
        return None

    cx, cy, radius = initial
    residuals = np.abs(np.hypot(x - cx, y - cy) - radius)
    threshold = max(1.5, float(np.median(residuals)) * 3.0)
    inliers = residuals <= threshold

    if np.count_nonzero(inliers) < 20:
        return None

    final = fit(x[inliers], y[inliers])

    if final is None:
        return None

    cx, cy, radius = final
    errors = np.abs(
        np.hypot(x[inliers] - cx, y[inliers] - cy) - radius
    )

    return {
        "cx": float(cx),
        "cy": float(cy),
        "radius": radius,
        "diameter": radius * 2.0,
        "fit_error_px": float(np.mean(errors)),
        "points": int(np.count_nonzero(inliers)),
    }


def _failure(status, reason):
    """Return a consistent result when measurement cannot be completed."""
    return {
        "status": status,
        "reason": reason,
        "od_px": None,
        "id_px": None,
        "units": "pixels",
        "validated": False,
        "quality_checks": {},
    }


def measure_od_id(roi, edges):
    """
    Estimate OD and ID in pixels using Hough circles and robust fitting.

    Quality checks are provisional geometric screens, not proof of
    physical dimensional accuracy.
    """
    if roi is None or roi.size == 0:
        raise ValueError("Product ROI is empty")

    if edges is None or edges.size == 0:
        raise ValueError("Edge image is empty")

    if roi.ndim != 3 or roi.shape[2] != 3:
        raise ValueError("Product ROI must be a 3-channel BGR image")

    if roi.shape[:2] != edges.shape[:2]:
        raise ValueError(
            f"ROI and edge dimensions differ: "
            f"{roi.shape[:2]} vs {edges.shape[:2]}"
        )

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
        return _failure(
            "no_circles_detected",
            "Hough circle detection found no candidates.",
        )

    circles = np.round(circles[0]).astype(int)
    ys, xs = np.where(edges > 0)
    edge_points = np.column_stack((xs, ys))

    if len(edge_points) < 40:
        return _failure(
            "insufficient_edge_points",
            "Too few edge pixels are available for fitting.",
        )

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
        return _failure(
            "no_valid_circle_pair",
            "No plausible concentric ID/OD candidate pair was found.",
        )

    _, cx, cy, inner_radius, outer_radius = min(
        pairs, key=lambda pair: pair[0]
    )

    radial_distances = np.hypot(
        edge_points[:, 0] - cx,
        edge_points[:, 1] - cy,
    )

    id_points = edge_points[
        np.abs(radial_distances - inner_radius) <= 4.0
    ]
    od_points = edge_points[
        np.abs(radial_distances - outer_radius) <= 4.0
    ]

    id_fit = fit_circle_robust(id_points)
    od_fit = fit_circle_robust(od_points)

    if id_fit is None or od_fit is None:
        return _failure(
            "circle_fit_failed",
            "Insufficient suitable points or unstable circle fitting.",
        )

    center_difference = float(
        np.hypot(
            id_fit["cx"] - od_fit["cx"],
            id_fit["cy"] - od_fit["cy"],
        )
    )

    ratio = id_fit["diameter"] / od_fit["diameter"]

    
    quality = check_measurement_quality(
        id_fit_error_px=id_fit["fit_error_px"],
        od_fit_error_px=od_fit["fit_error_px"],
        center_difference_px=center_difference,
        id_od_ratio=ratio,
    )

    quality_checks = quality["checks"]
    failure_reasons = quality["failure_reasons"]

    result = {
        "status": (
            "estimated" if not failure_reasons
            else "quality_check_failed"
        ),
        "od_px": round(od_fit["diameter"], 2),
        "id_px": round(id_fit["diameter"], 2),
        "od_center_x": od_fit["cx"],
        "od_center_y": od_fit["cy"],
        "id_center_x": id_fit["cx"],
        "id_center_y": id_fit["cy"],
        "od_radius_px": od_fit["radius"],
        "id_radius_px": id_fit["radius"],
        "od_fit_error_px": round(od_fit["fit_error_px"], 3),
        "id_fit_error_px": round(id_fit["fit_error_px"], 3),
        "od_fit_points": od_fit["points"],
        "id_fit_points": id_fit["points"],
        "center_difference_px": round(center_difference, 3),
        "id_od_ratio": round(ratio, 4),
        "quality_checks": quality_checks,
        "failure_reasons": failure_reasons,
        "units": "pixels",
        "validated": False,
        "method": "Hough pair + robust circle fit",
    }

    return result
