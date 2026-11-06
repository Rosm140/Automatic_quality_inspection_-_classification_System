
import cv2
import numpy as np


# Provisional geometric screening limits.
# These are not validated industrial acceptance limits.
MAX_FIT_ERROR_PX = 2.5
MAX_CENTER_DIFFERENCE_PX = 3.0
MIN_ID_OD_RATIO = 0.55
MAX_ID_OD_RATIO = 0.90
NOMINAL_ID_OD_RATIO = 9.652 / 12.7
MAX_NOMINAL_RATIO_DEVIATION = 0.03

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
        "nominal_ratio_consistency_ok": (
            np.isfinite(id_od_ratio)
            and abs(id_od_ratio - NOMINAL_ID_OD_RATIO)
            <= MAX_NOMINAL_RATIO_DEVIATION
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
    Estimate ID/OD from radial edge peaks around the ROI center.
    Returns pixel estimates; not validated physical measurements.
    """
    if roi is None or roi.size == 0:
        raise ValueError("Product ROI is empty")

    if edges is None or edges.size == 0:
        raise ValueError("Edge image is empty")

    if roi.ndim != 3 or roi.shape[2] != 3:
        raise ValueError("Product ROI must be a 3-channel BGR image")

    if roi.shape[:2] != edges.shape[:2]:
        raise ValueError("ROI and edge dimensions differ")

    h, w = edges.shape[:2]
    cx0, cy0 = w / 2.0, h / 2.0

    ys, xs = np.where(edges > 0)
    if len(xs) < 40:
        return _failure(
            "insufficient_edge_points",
            "Too few edge pixels are available for fitting.",
        )

    # Radial distance of every edge pixel from the ROI center.
    distances = np.hypot(xs - cx0, ys - cy0)

    # Create a radial histogram; circular boundaries create peaks.
    max_radius = min(h, w) / 2.0
    bins = np.arange(0, max_radius + 1.0, 1.0)
    counts, bin_edges = np.histogram(distances, bins=bins)
    radii = (bin_edges[:-1] + bin_edges[1:]) / 2.0

    # Find local peaks with enough edge support.
    peaks = []
    for i in range(2, len(counts) - 2):
        if (
            counts[i] >= counts[i - 1]
            and counts[i] >= counts[i + 1]
            and counts[i] >= 8
            and 15 <= radii[i] <= max_radius - 2
        ):
            peaks.append((float(radii[i]), int(counts[i])))

    if len(peaks) < 2:
        return _failure(
            "insufficient_radial_peaks",
            "Could not identify two circular edge boundaries.",
        )

    # Keep strong peaks, then evaluate plausible inner/outer pairs.
    peaks.sort(key=lambda p: p[1], reverse=True)
    peaks = peaks[:20]

    expected_ratio = 0.380 / 0.500
    pairs = []

    for inner_radius, inner_support in peaks:
        for outer_radius, outer_support in peaks:
            if outer_radius <= inner_radius:
                continue

            ratio = inner_radius / outer_radius
            if not 0.55 <= ratio <= 0.90:
                continue

            # Prefer the expected ratio, with edge support as a tie-breaker.
            score = (
                abs(ratio - expected_ratio) * 2.0
                - (inner_support + outer_support) / 1000.0
            )

            pairs.append(
                (
                    score,
                    inner_radius,
                    outer_radius,
                )
            )

    if not pairs:
        return _failure(
            "no_valid_radial_pair",
            "No plausible inner/outer radial edge pair was found.",
        )

    print("\n--- RADIAL PAIR CANDIDATES ---")
    for score, inner_r, outer_r in sorted(pairs, key=lambda p: p[0])[:10]:
        print(
            f"ID radius={inner_r:.1f}, "
            f"OD radius={outer_r:.1f}, "
            f"ratio={inner_r / outer_r:.4f}, "
            f"score={score:.4f}"
        )
    print("-----------------------------\n")

    _, inner_radius, outer_radius = min(
        pairs, key=lambda p: p[0]
    )

    # Select edge pixels near each radial peak.
    id_mask = np.abs(distances - inner_radius) <= 2.5
    od_mask = np.abs(distances - outer_radius) <= 2.5

    id_points = np.column_stack((xs[id_mask], ys[id_mask]))
    od_points = np.column_stack((xs[od_mask], ys[od_mask]))

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

    print("\n--- MEASUREMENT DEBUG ---")
    print("ROI size:", w, "x", h)
    print("ROI center:", cx0, cy0)
    print("Selected ID radius:", inner_radius)
    print("Selected OD radius:", outer_radius)
    print("ID fit:", id_fit)
    print("OD fit:", od_fit)
    print("ID/OD ratio:", ratio)
    print("Quality checks:", quality_checks)
    print("Failure reasons:", failure_reasons)
    print("-------------------------\n")

    return {
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
        "method": "Radial edge peaks + robust circle fit",
    }

    
