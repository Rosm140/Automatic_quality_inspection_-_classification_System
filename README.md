# AI-Based Visual & Dimensional Quality Inspection System

> An intelligent machine vision system for automated visual inspection and dimensional measurement of machined industrial components using **YOLOv8**, **OpenCV**, **ESP32**, and a **Sony IMX335 Camera**.

---

## 📌 Project Overview

This project aims to automate the quality inspection process of machined metal components by combining Artificial Intelligence, Computer Vision, and Embedded Systems.

Unlike traditional inspection systems that only classify defects, this system performs both:

- Visual Inspection
- Dimensional Inspection

The complete inspection process is automated from image capture to defect classification and product rejection.

---

## 🎯 Objectives

- Detect the correct product using YOLOv8.
- Identify incorrect or missing components.
- Measure critical dimensions using OpenCV.
- Inspect visual defects such as scratches, cracks, and burrs.
- Verify engineering tolerances.
- Automatically classify products as PASS or FAIL.
- Communicate inspection results to ESP32.
- Trigger a servo mechanism to reject defective products.

---

# System Workflow

```
Product Placement
        │
        ▼
Sony IMX335 Camera
        │
        ▼
YOLOv8 Product Detection
        │
        ▼
ROI Extraction
        │
        ▼
Dimensional Measurement
(OpenCV)
        │
        ▼
Feature Inspection
        │
        ▼
Surface Inspection
        │
        ▼
Decision Engine
        │
        ▼
PASS / FAIL
        │
        ▼
ESP32
        │
        ▼
Servo Motor
```

---

# Key Features

## Product Detection

- Multi-product support
- Automatic product identification
- Wrong product detection

## Dimensional Measurement

- Outer Diameter (OD)
- Inner Diameter (ID)
- Width
- Height
- Groove dimensions
- Hole diameter
- Chamfer verification

## Feature Inspection

- Hole detection
- Slot detection
- Groove detection
- Missing feature detection

## Surface Inspection

- Scratch detection
- Crack detection
- Burr detection
- Surface anomaly detection

## Hardware Integration

- Sony IMX335 Camera
- ESP32
- IR Sensor
- Servo Motor
- LED Ring Light

---

# Technology Stack

## Artificial Intelligence

- YOLOv8

## Computer Vision

- OpenCV
- NumPy

## Programming

- Python

## Embedded System

- ESP32
- Arduino IDE

## Dataset

- Roboflow

## Version Control

- Git
- GitHub

---

# Hardware

| Component | Description |
|------------|-------------|
| Sony IMX335 Camera | Image Acquisition |
| ESP32 | Hardware Controller |
| MG996R Servo | Product Rejection |
| IR Sensor | Product Trigger |
| LED Ring Light | Uniform Illumination |
| Laptop | AI Processing |

---

# Project Structure

```
AI_Visual_Dimensional_Inspection_System/

├── config/
├── data/
│   ├── raw/
│   ├── labeled/
│   ├── calibration/
│   ├── test/
│   └── edge_cases/
│
├── detection/
├── measurement/
├── calibration/
├── communication/
├── dashboard/
├── database/
│
├── docs/
│   ├── hardware/
│   ├── products/
│   ├── diagrams/
│   ├── logbook/
│   └── reports/
│
├── models/
├── notebooks/
├── arduino/
├── tests/
├── assets/
├── logs/
│
├── README.md
├── requirements.txt
└── .gitignore
```

---

# Development Roadmap

## Phase 1

Project Planning & Documentation

## Phase 2

Hardware Setup

## Phase 3

Camera Calibration

## Phase 4

Dataset Collection

## Phase 5

YOLO Training

## Phase 6

Measurement Module

## Phase 7

Feature Inspection

## Phase 8

Surface Inspection

## Phase 9

System Integration

## Phase 10

Testing & Validation

## Phase 11

Dashboard & Reporting

## Phase 12

Final Deployment

---

# Team

## Member A (Rohit)

Role:

- Team Leader
- AI Development
- OpenCV
- YOLO
- System Integration

---

## Member B (Sneha)

Role:

- Hardware
- ESP32
- Servo
- Camera Setup

---

## Member C (Vaibhav)

Role:

- Dataset Engineering
- Roboflow
- Product Database

---

## Member D (Komal)

Role:

- Documentation
- Testing
- Quality Assurance

---

# Git Workflow

Each member works on a separate branch.

Example:

```
main (Architecture & Lead)

feature/hardware

feature/dataset

feature/documentation
```

Workflow:

1. Pull latest changes
2. Create/Update branch
3. Commit changes
4. Push branch
5. Open Pull Request
6. Team Leader reviews
7. Merge into main

---

# Branch Naming Convention

```
main

feature/hardware

feature/dataset

feature/documentation
```

---

# Commit Message Format

```
Sprint1-Day1-Architecture

Sprint1-Day1-Hardware

Sprint1-Day1-Dataset

Sprint1-Day1-Documentation
```

---

# Future Improvements

- Multi-camera support
- Industrial camera integration
- PLC communication
- Real-time dashboard
- Cloud monitoring
- AI model optimization
- Edge AI deployment
- Multi-product inspection

---

# License

This project is developed for academic research and industrial learning purposes.

---

# Acknowledgements

This project is developed as a Final Year Engineering Project to explore practical applications of Artificial Intelligence, Computer Vision, and Embedded Systems in automated industrial quality inspection.