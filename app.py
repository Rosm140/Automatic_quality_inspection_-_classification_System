
import json
import tempfile
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import streamlit as st

from src.measurement.pipeline import inspect_image
from src.measurement.dimensional_measurement import measure_od_id


st.set_page_config(
    page_title="Industrial Quality Inspection",
    page_icon="🔍",
    layout="wide",
)

st.title("Industrial Quality Inspection System")
st.caption(
    "Prototype dashboard | Dimensional measurement using computer vision"
)

st.info(
    "Current capabilities: OD/ID estimation in pixels and geometric quality "
    "checks. AI-based product identification, surface-defect detection, and "
    "validated industrial PASS/FAIL decisions are not implemented."
)

uploaded_file = st.file_uploader(
    "Upload a product image",
    type=["jpg", "jpeg", "png", "bmp"],
)

if uploaded_file is not None:
    file_bytes = np.frombuffer(uploaded_file.getvalue(), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    if image is None:
        st.error("The uploaded file could not be read as an image.")
        st.stop()

    height, width = image.shape[:2]

    st.subheader("Input Image")
    left, right = st.columns([1, 1])

    with left:
        st.image(
            cv2.cvtColor(image, cv2.COLOR_BGR2RGB),
            caption=f"Uploaded image — {width} × {height} pixels",
            use_container_width=True,
        )

    if st.button("Run Dimensional Inspection", type="primary"):
        with st.spinner("Processing image..."):
            result = None
            measurement = None
            processed_image = image.copy()

            # Save a temporary copy so the existing pipeline can be reused.
            try:
                suffix = Path(uploaded_file.name).suffix.lower()
                if suffix not in [".jpg", ".jpeg", ".png", ".bmp"]:
                    suffix = ".jpg"

                with tempfile.NamedTemporaryFile(
                    suffix=suffix, delete=False
                ) as temp_file:
                    temp_path = Path(temp_file.name)
                    temp_file.write(uploaded_file.getvalue())

                try:
                    result = inspect_image(temp_path)
                finally:
                    temp_path.unlink(missing_ok=True)

                # Match the existing pipeline's undistortion behavior.
                # Use the same resolution check and calibration function.
                from src.measurement.undistortion import (
                    load_calibration,
                    undistort_image,
                )

                measurement_image = image.copy()

                try:
                    _, _, metadata = load_calibration()
                    resolution = metadata["resolution"]
                    expected_size = (
                        int(resolution["width"]),
                        int(resolution["height"]),
                    )

                    if (width, height) == expected_size:
                        measurement_image = undistort_image(measurement_image)

                except (
                    FileNotFoundError,
                    KeyError,
                    TypeError,
                    ValueError,
                    OSError,
                ):
                    pass

                gray = cv2.cvtColor(
                    measurement_image, cv2.COLOR_BGR2GRAY
                )
                edges = cv2.Canny(gray, 50, 150)

                measurement = measure_od_id(measurement_image, edges)

                # Draw circles using the actual fitted centers and radii.
                if (
                    measurement.get("od_px") is not None
                    and measurement.get("id_px") is not None
                    and all(
                        measurement.get(key) is not None
                        for key in [
                            "od_center_x",
                            "od_center_y",
                            "id_center_x",
                            "id_center_y",
                            "od_radius_px",
                            "id_radius_px",
                        ]
                    )
                ):
                    processed_image = measurement_image.copy()

                    od_center = (
                        round(measurement["od_center_x"]),
                        round(measurement["od_center_y"]),
                    )
                    id_center = (
                        round(measurement["id_center_x"]),
                        round(measurement["id_center_y"]),
                    )

                    cv2.circle(
                        processed_image,
                        od_center,
                        round(measurement["od_radius_px"]),
                        (0, 255, 0),
                        2,
                    )
                    cv2.circle(
                        processed_image,
                        id_center,
                        round(measurement["id_radius_px"]),
                        (255, 0, 0),
                        2,
                    )

                    cv2.circle(
                        processed_image, od_center, 4, (0, 255, 255), -1
                    )
                    cv2.circle(
                        processed_image, id_center, 4, (0, 255, 255), -1
                    )

            except Exception as exc:
                st.error(f"Inspection failed: {exc}")
                st.exception(exc)
                st.stop()

        st.session_state["inspection_result"] = result
        st.session_state["measurement_result"] = measurement
        st.session_state["overlay_image"] = processed_image
        st.session_state["edges_image"] = edges

    result = st.session_state.get("inspection_result")
    measurement = st.session_state.get("measurement_result")

    if result is not None and measurement is not None:
        st.divider()
        st.subheader("Inspection Results")

        if result.get("processing_status") == "completed":
            st.success("Image processing completed")
        else:
            st.warning("Measurement could not be completed by the pipeline")

        od = measurement.get("od_px")
        inner_diameter = measurement.get("id_px")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Outer Diameter (OD)",
            f"{od:.2f} px" if od is not None else "Unavailable",
        )
        col2.metric(
            "Inner Diameter (ID)",
            f"{inner_diameter:.2f} px"
            if inner_diameter is not None
            else "Unavailable",
        )

        ratio = measurement.get("id_od_ratio")
        col3.metric(
            "ID / OD Ratio",
            f"{ratio:.4f}" if ratio is not None else "Unavailable",
        )

        st.caption(
            "Measurements are pixel estimates. They are not validated "
            "physical dimensions in millimetres."
        )

        image_col, edge_col = st.columns(2)

        with image_col:
            st.markdown("#### Fitted-Circle Overlay")
            st.image(
                cv2.cvtColor(
                    st.session_state["overlay_image"], cv2.COLOR_BGR2RGB
                ),
                use_container_width=True,
            )

        with edge_col:
            st.markdown("#### Canny Edge Image")
            st.image(
                st.session_state["edges_image"],
                clamp=True,
                use_container_width=True,
            )

        st.markdown("#### Geometric Quality Checks")

        checks = measurement.get("quality_checks", {})

        if checks:
            check_rows = [
                {
                    "Check": name.replace("_", " ").title(),
                    "Result": "PASS" if passed else "FAIL",
                }
                for name, passed in checks.items()
            ]
            st.dataframe(
                pd.DataFrame(check_rows),
                use_container_width=True,
                hide_index=True,
            )

            if measurement.get("status") == "estimated":
                st.success("All configured geometric checks passed.")
            else:
                st.warning(
                    "One or more geometric checks failed. "
                    "Review the measurement before using it."
                )
        else:
            st.warning(
                measurement.get(
                    "reason",
                    "Quality checks were unavailable for this image.",
                )
            )

        details = {
            "pipeline_result": result,
            "measurement_details": measurement,
        }

        st.markdown("#### Measurement Details")
        st.json(details)

        json_bytes = json.dumps(details, indent=2).encode("utf-8")

        st.download_button(
            "Download Results (JSON)",
            data=json_bytes,
            file_name="inspection_results.json",
            mime="application/json",
        )

        if od is not None and inner_diameter is not None:
            csv_df = pd.DataFrame(
                [
                    {
                        "image": uploaded_file.name,
                        "outer_diameter_px": od,
                        "inner_diameter_px": inner_diameter,
                        "id_od_ratio": ratio,
                        "center_difference_px": measurement.get(
                            "center_difference_px"
                        ),
                        "measurement_status": measurement.get("status"),
                        "physical_validation": "NOT_VALIDATED",
                    }
                ]
            )

            st.download_button(
                "Download Results (CSV)",
                data=csv_df.to_csv(index=False).encode("utf-8"),
                file_name="inspection_results.csv",
                mime="text/csv",
            )

st.divider()
st.caption(
    "Prototype only. Geometric checks are provisional and do not establish "
    "industrial conformity or product acceptance."
)
