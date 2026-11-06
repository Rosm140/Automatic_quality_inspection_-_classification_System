from database.db_manager import save_inspection, get_inspection_history, get_inspection_statistics
import json
import tempfile
from pathlib import Path
import time

import cv2
import numpy as np
import pandas as pd
import streamlit as st

from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
from src.measurement.pipeline import inspect_image
from src.measurement.dimensional_measurement import measure_od_id
from src.utils.config_loader import load_config

class CameraProcessor(VideoProcessorBase):
    def __init__(self):
        self.frame = None

    def recv(self, frame):
        self.frame = frame.to_ndarray(format="bgr24")
        return frame

calibration_config = load_config("calibration.yaml")
PIXELS_PER_MM = float(
    calibration_config["calibration"]["scale"]["pixels_per_mm"]
)

st.set_page_config(
    page_title="Industrial Quality Inspection",
    page_icon="🔍",
    layout="wide",
)

st.title("Industrial Quality Inspection System")
st.caption(
    "Prototype dashboard | Dimensional measurement using computer vision"
)

# Dashboard statistics from the inspection database
st.divider()
st.subheader("Production Overview")

stats = get_inspection_statistics()
history = get_inspection_history(500)

total = stats["total_inspections"]
completed = stats["completed_inspections"]
failed = stats["failed_inspections"]

col1, col2, col3 = st.columns(3)

col1.metric("Total Inspections", total)
col2.metric("Processing Completed", completed)
col3.metric("Processing Failed", failed)

st.caption(
    "These statistics represent saved inspection attempts, "
    "not confirmed good or defective products."
)

st.subheader("Recent Inspection History")

if history:
    history_df = pd.DataFrame(history)

    st.dataframe(
        history_df,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "Download Complete Inspection History (CSV)",
        data=history_df.to_csv(index=False).encode("utf-8"),
        file_name="inspection_history.csv",
        mime="text/csv",
    )
else:
    st.info("No inspections have been recorded yet.")

st.info(
    "Current capabilities: OD/ID estimation in pixels and geometric quality "
    "checks. AI-based product identification, surface-defect detection, and "
    "validated industrial PASS/FAIL decisions are not implemented."
)

st.subheader("Inspection Configuration")

inspection_orientation = st.selectbox(
    "Inspection Orientation",
    options=["Vertical", "Horizontal"],
    index=0,
    help="Select the orientation for this inspection."
)

inspection_orientation = inspection_orientation.lower()

# Camera Inspection
st.subheader("Camera Inspection")

camera_enabled = st.checkbox("Use camera for inspection")

if camera_enabled:
    ctx = webrtc_streamer(
        key="product-camera",
        video_processor_factory=CameraProcessor,
        media_stream_constraints={
            "video": True,
            "audio": False,
        },
        async_processing=True,
    )

    if ctx.video_processor:
        st.info("Camera connected. Position the product and click Capture.")

        if st.button("Capture Product", key="capture_product"):
            with st.spinner("Waiting 4 seconds... Move your hand away."):
                time.sleep(4)

                processor = ctx.video_processor
                captured_image = processor.frame

                if captured_image is None:
                    st.error("No camera frame available. Check the camera.")
                else:
                    captured_image = captured_image.copy()

                    # Store the captured image for the shared inspection pipeline.
                    st.session_state["pending_inspection_image"] = captured_image
                    st.session_state["pending_inspection_filename"] = "camera_capture.jpg"
                    st.session_state["inspection_source"] = "camera"

                    st.rerun()

uploaded_file = st.file_uploader(
    "Upload a product image",
    type=["jpg", "jpeg", "png", "bmp"],
)

camera_pending = (
    st.session_state.get("pending_inspection_image") is not None
)

if uploaded_file is not None or camera_pending:
    if camera_pending:
        image = st.session_state["pending_inspection_image"].copy()
        image_filename = st.session_state.get(
            "pending_inspection_filename",
            "camera_capture.jpg",
        )
    else:
        file_bytes = np.frombuffer(
            uploaded_file.getvalue(),
            dtype=np.uint8,
        )
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        image_filename = uploaded_file.name

    if image is None:
        st.error("The input image could not be read.")
        st.stop()

    height, width = image.shape[:2]

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

    run_inspection_now = camera_pending or st.button(
        "Run Dimensional Inspection",
        type="primary",
    )

    if run_inspection_now:
        with st.spinner("Processing image..."):
            result = None
            measurement = None
            processed_image = image.copy()

            # Save a temporary copy so the existing pipeline can be reused.
            try:
                suffix = Path(image_filename).suffix.lower()

                if suffix not in [".jpg", ".jpeg", ".png", ".bmp"]:
                    suffix = ".jpg"

                success, encoded_image = cv2.imencode(
                    suffix,
                    image,
                )

                if not success:
                    raise ValueError("Could not encode the inspection image.")

                with tempfile.NamedTemporaryFile(
                    suffix=suffix,
                    delete=False,
                ) as temp_file:
                    temp_path = Path(temp_file.name)
                    temp_file.write(encoded_image.tobytes())
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

               
                # Step 1: Convert the undistorted image to grayscale
                gray_full = cv2.cvtColor(
                    measurement_image, cv2.COLOR_BGR2GRAY
                )

                # Step 2: Smooth the image to reduce noise
                blurred = cv2.GaussianBlur(
                    gray_full, (9, 9), 2
                )

                # Step 3: Detect circular product boundary
                image_h, image_w = gray_full.shape[:2]

                circles = cv2.HoughCircles(
                    blurred,
                    cv2.HOUGH_GRADIENT,
                    dp=1.2,
                    minDist=min(image_h, image_w) // 4,
                    param1=100,
                    param2=28,
                    minRadius=10,
                    maxRadius=min(image_h, image_w) // 4,
                )

                # Step 4: Extract ROI around the detected circle
                if circles is not None:
                    circles = np.round(circles[0]).astype(int)

                    # Choose the detected circle closest to the image center
                    image_center_x = image_w // 2
                    image_center_y = image_h // 2

                    circle_x, circle_y, circle_radius = min(
                        circles,
                        key=lambda c: (
                            (c[0] - image_center_x) ** 2
                            + (c[1] - image_center_y) ** 2
                        ),
                    )

                    # Add margin around the detected product
                    roi_radius = 50

                    x1 = max(0, circle_x - roi_radius)
                    y1 = max(0, circle_y - roi_radius)
                    x2 = min(image_w, circle_x + roi_radius)
                    y2 = min(image_h, circle_y + roi_radius)

                    measurement_image = measurement_image[y1:y2, x1:x2]

                    print("\n--- ROI DEBUG ---")
                    print("Full image size:", image_w, "x", image_h)
                    print("Hough circles:", circles)
                    print("Selected circle:", circle_x, circle_y, circle_radius)
                    print("ROI bounds:", x1, y1, x2, y2)
                    print("ROI dimensions:", measurement_image.shape[1], "x", measurement_image.shape[0])
                    print("-----------------\n")

                    st.success("Product ROI extracted successfully.")

                else:
                    st.warning(
                        "Circular product not detected. "
                        "Measurement is being attempted on the full image."
                    )

                # Step 5: Edge detection on the extracted ROI
                gray = cv2.cvtColor(
                    measurement_image, cv2.COLOR_BGR2GRAY
                )

                edges = cv2.Canny(gray, 50, 150)

                # Step 6: Measure OD and ID within the ROI
                measurement = measure_od_id(measurement_image, edges)


                od_px = measurement.get("od_px")
                id_px = measurement.get("id_px")

                od_mm = od_px / PIXELS_PER_MM if od_px is not None else None
                id_mm = id_px / PIXELS_PER_MM if id_px is not None else None

                measurement["od_mm"] = od_mm
                measurement["id_mm"] = id_mm

                # Keep the pipeline result consistent with the ROI measurement.
                result["od_px"] = od_px
                result["id_px"] = id_px
                result["od_mm"] = od_mm
                result["id_mm"] = id_mm
                result["measurement_status"] = measurement.get("status")
                result["id_od_ratio"] = measurement.get("id_od_ratio")
                result["center_difference_px"] = measurement.get(
                    "center_difference_px"
                )

                if measurement.get("status") == "estimated":
                    result["processing_status"] = "completed"
                else:
                    result["processing_status"] = "quality_check_failed"
                    result["measurement_reason"] = measurement.get(
                        "reason",
                        "Geometric quality checks did not pass."
                    )

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

        # Save this inspection to the database.
        try:
            inspection_id = save_inspection(
                image_filename=image_filename,
                processing_status=result.get(
                    "processing_status", "failed"
                ),
                od_px=od_px,
                id_px=id_px,
                od_mm=od_mm,
                id_mm=id_mm,
                measurement_status=measurement.get("status"),
                center_difference_px=measurement.get(
                    "center_difference_px"
                ),
                id_od_ratio=measurement.get("id_od_ratio"),
                defect_detection_status="NOT_IMPLEMENTED",
                inspection_orientation=inspection_orientation,
            )

            st.success(
                f"Inspection #{inspection_id} saved successfully."
            )

        except Exception as exc:
            st.error(f"Could not save inspection to database: {exc}")

        # Keep the results available for display.
        st.session_state["inspection_result"] = result
        st.session_state["measurement_result"] = measurement
        st.session_state["overlay_image"] = processed_image
        st.session_state["edges_image"] = edges
        if camera_pending:
            st.session_state.pop("pending_inspection_image", None)
            st.session_state.pop("pending_inspection_filename", None)

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

        od_mm = measurement.get("od_mm")
        id_mm = measurement.get("id_mm")

        col1.metric(
            "Outer Diameter (OD)",
            f"{od_mm:.2f} mm" if od_mm is not None else "Unavailable",
            delta=f"{od:.2f} px" if od is not None else None,
            )

        col2.metric(
            "Inner Diameter (ID)",
            f"{id_mm:.2f} mm" if id_mm is not None else "Unavailable",
            delta=f"{inner_diameter:.2f} px"
            if inner_diameter is not None
            else None,
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
                caption="Canny edges extracted from the product ROI",
                clamp=True,
                width="stretch",
            )
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
                st.success("Geometric measurement completed")
            else:
                st.warning(
                    "Measurement requires review: "
                    + measurement.get("reason", "Quality checks did not pass.")
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
                        "image": image_filename, 
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
