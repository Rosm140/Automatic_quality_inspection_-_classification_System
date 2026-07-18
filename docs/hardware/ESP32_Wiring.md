# Camera Setup Documentation

## Camera

Sony IMX335 USB Camera

---

# Camera Specifications

Sensor: Sony IMX335 CMOS

Resolution:
2592 × 1944 (5 MP)

Frame Rate:
30 FPS (Maximum)

Interface:
USB 3.0

Lens:
Fixed Focus / Manual Focus (depending on module)

Field of View:
Approximately 80°

---

# Working Distance

Recommended Distance:

250–350 mm

This distance provides:

- Complete product visibility
- High image sharpness
- Minimal perspective distortion

---

# Camera Mounting Position

Top View (90°)

The camera should be mounted directly above the inspection area.

Benefits:

- Eliminates perspective distortion
- Improves dimensional measurement
- Consistent object orientation

---

# Focus Method

Preferred Method:

Manual Focus

Reasons:

- Once calibrated, focus remains constant.
- No autofocus delay.
- Better repeatability.
- Suitable for industrial inspection.

---

# Lighting Arrangement

Lighting Type:

Diffuse White LED Ring Light

Position:

Around the camera lens.

Alternative:

LED panel positioned at 45° from both sides.

Advantages:

- Eliminates shadows
- Reduces reflections
- Produces consistent images

---

# Background Requirements

Material:

White Matte Acrylic Sheet

Requirements:

- Non-reflective
- Dust-free
- Flat surface
- Uniform white color

Reason:

Provides maximum contrast for object detection and simplifies image segmentation.

---

# Research Notes

## Why Industrial Vision Systems Use Fixed Lighting and Fixed Camera Positions

Industrial machine vision systems require highly repeatable image acquisition. Even small changes in camera angle or lighting can affect image quality, object appearance, and measurement accuracy.

### Fixed Camera Position

A fixed camera ensures:

- Constant field of view
- Identical object perspective
- Accurate dimensional measurements
- Reliable defect detection
- Consistent calibration

If the camera moves, the object's size and shape in the captured image may change, leading to incorrect measurements or missed defects.

### Fixed Lighting

Lighting significantly influences image quality. Consistent lighting provides:

- Stable brightness
- Reduced shadows
- Minimized reflections
- Better edge detection
- Consistent color representation

Changing light intensity or direction can create false edges, alter object appearance, or hide small defects such as cracks or scratches.

### Importance in AI-Based Inspection

YOLOv8 and OpenCV perform best when input images are consistent. Fixed lighting and camera positioning reduce unnecessary variations, enabling the AI model to focus on actual product defects rather than environmental changes.

### Conclusion

Using a fixed camera position and controlled lighting improves measurement accuracy, defect detection reliability, and overall system repeatability, making them essential practices in industrial machine vision systems.