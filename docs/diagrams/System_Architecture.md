# System Architecture

## Overview

The AI-Based Visual & Dimensional Quality Inspection System is a modular machine vision platform designed to automate industrial quality inspection. The system combines Artificial Intelligence, Computer Vision, and Embedded Systems to inspect products, measure dimensions, detect defects, and automatically reject defective parts.

---

# High-Level Architecture

```
                  ┌─────────────────────┐
                  │  Industrial Product │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │     IR Sensor       │
                  │ Product Detection   │
                  └──────────┬──────────┘
                             │ Trigger
                             ▼
                  ┌─────────────────────┐
                  │ Sony IMX335 Camera  │
                  │ Capture Image       │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Image Acquisition   │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ YOLOv8 Detection    │
                  │ Product Localization│
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ ROI Extraction      │
                  └──────────┬──────────┘
                             │
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
 ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
 │Measurement     │  │Feature         │  │Surface         │
 │Module          │  │Inspection      │  │Inspection      │
 │OpenCV          │  │OpenCV          │  │OpenCV / AI     │
 └────────┬───────┘  └────────┬───────┘  └────────┬───────┘
          └──────────────────┼──────────────────┘
                             ▼
                  ┌─────────────────────┐
                  │ Decision Engine     │
                  │ PASS / FAIL         │
                  └──────────┬──────────┘
                             │
                  ┌──────────┴──────────┐
                  ▼                     ▼
          Store Results          ESP32 Controller
                                        │
                                        ▼
                                 Servo Motor
                                        │
                                        ▼
                               Reject Defective Part
```

---

# Module Descriptions

## 1. Product Trigger

The IR Sensor detects when a product reaches the inspection area and triggers the image acquisition process.

---

## 2. Image Acquisition

The Sony IMX335 USB Camera captures a high-resolution image under controlled lighting conditions.

---

## 3. Product Detection

YOLOv8 identifies the product and returns its bounding box coordinates.

Output:

- Product Class
- Confidence Score
- Bounding Box

---

## 4. ROI Extraction

The Region of Interest (ROI) is cropped from the original image to reduce unnecessary processing and improve inspection accuracy.

---

## 5. Dimensional Measurement

OpenCV performs geometric measurements such as:

- Outer Diameter (OD)
- Inner Diameter (ID)
- Width
- Height
- Hole Diameter
- Groove Width

Measurements are converted from pixels to millimeters using camera calibration.

---

## 6. Feature Inspection

Checks for the presence or absence of required features:

- Holes
- Slots
- Grooves
- Chamfers

---

## 7. Surface Inspection

Inspects the product surface for defects:

- Scratch
- Crack
- Burr
- Surface Damage

---

## 8. Decision Engine

Combines the outputs of all inspection modules.

Decision Rules:

- Correct Product
- Dimensions Within Tolerance
- Required Features Present
- No Surface Defects

If all conditions pass:

PASS

Otherwise:

FAIL

---

## 9. ESP32 Communication

The software sends a serial command:

PASS

or

FAIL

to the ESP32 controller.

---

## 10. Servo Rejection System

If the ESP32 receives a FAIL command, it rotates the servo motor to reject the defective product.

PASS products continue on the conveyor.

---

# Future Expansion

The architecture is designed to support:

- Multiple cameras
- PLC Integration
- Industrial cameras
- Barcode Scanner
- Cloud Dashboard
- Database Logging
- Production Statistics
- Predictive Maintenance

---

# Advantages of Modular Architecture

- Independent module development
- Easy debugging
- Scalable design
- Easier testing
- Easy maintenance
- Supports future industrial deployment

---

# Current Technology Stack

| Module | Technology |
|----------|------------|
| Product Detection | YOLOv8 |
| Measurements | OpenCV |
| Feature Inspection | OpenCV |
| Surface Inspection | OpenCV + AI |
| Controller | ESP32 |
| Communication | PySerial |
| Programming | Python |
| Version Control | Git & GitHub |