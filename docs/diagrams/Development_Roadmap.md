# Development Roadmap

## Project Timeline

**Project Duration:** 12 Weeks (Maximum)

**Development Methodology:** Agile Sprint Model

**Sprint Duration:** Flexible

> If a sprint is completed and approved before the scheduled week ends, the team immediately begins the next sprint. We do not wait for the calendar.

---

# Milestone 1
## Project Foundation

Duration:
Week 1

### Objectives

- Project planning
- GitHub repository setup
- Documentation
- System architecture
- Hardware documentation
- Product specification
- Coding standards

### Deliverables

- README
- Requirements
- Architecture
- Roadmap
- Documentation Templates

---

# Milestone 2
## Hardware & Vision Setup

Duration:
Week 2

### Objectives

- Camera installation
- Lighting setup
- ESP32 setup
- Servo testing
- IR sensor testing
- Camera calibration

### Deliverables

- Stable image acquisition
- Working ESP32 communication
- Camera calibration data

---

# Milestone 3
## Dataset Engineering

Duration:
Week 3

### Objectives

- Product image collection
- Image labeling
- Dataset organization
- Roboflow project
- Dataset versioning

### Deliverables

- Dataset Version 1
- Product classes
- Annotation files

---

# Milestone 4
## Product Detection

Duration:
Week 4

### Objectives

- YOLO training
- Validation
- Hyperparameter tuning
- Product localization

### Deliverables

- Trained YOLO model
- Detection accuracy report

---

# Milestone 5
## Dimensional Measurement

Duration:
Week 5

### Objectives

- Pixel calibration
- OD measurement
- ID measurement
- Width measurement
- Height measurement

### Deliverables

- Measurement module
- Calibration report

---

# Milestone 6
## Feature Inspection

Duration:
Week 6

### Objectives

Inspect:

- Holes
- Slots
- Grooves
- Chamfers

### Deliverables

Feature inspection module

---

# Milestone 7
## Surface Inspection

Duration:
Week 7

### Objectives

Detect:

- Scratch
- Crack
- Burr
- Surface damage

### Deliverables

Surface inspection module

---

# Milestone 8
## Decision Engine

Duration:
Week 8

### Objectives

Combine:

- YOLO
- Measurements
- Feature inspection
- Surface inspection

Generate:

PASS

FAIL

### Deliverables

Decision engine

---

# Milestone 9
## Hardware Integration

Duration:
Week 9

### Objectives

- Serial communication
- ESP32
- Servo rejection
- IR trigger

### Deliverables

Integrated inspection system

---

# Milestone 10
## Dashboard & Database

Duration:
Week 10

### Objectives

- Inspection history
- Statistics
- Dashboard
- Logging

### Deliverables

Dashboard Version 1

---

# Milestone 11
## Testing & Optimization

Duration:
Week 11

### Objectives

- Accuracy testing
- Speed testing
- Stress testing
- Bug fixing
- Optimization

### Deliverables

Testing report

---

# Milestone 12
## Final Delivery

Duration:
Week 12

### Objectives

- Final integration
- Documentation
- Presentation
- Demo
- Viva preparation

### Deliverables

Final working system

Final report

Presentation

GitHub Release v1.0

---

# Sprint Workflow

```
Sprint Assigned
        │
        ▼
Development
        │
        ▼
Git Commit
        │
        ▼
Pull Request
        │
        ▼
Review
        │
        ▼
Approved?
      │
 ┌────┴────┐
 │         │
Yes       No
 │         │
 ▼         ▼
Next    Fix Issues
Sprint
```

---

# Team Responsibilities

## Team Leader

- AI
- Architecture
- Integration
- Code Review

## Hardware Engineer

- ESP32
- Camera
- Wiring
- Servo

## Dataset Engineer

- Dataset
- Labeling
- Roboflow
- Product Specifications

## Documentation Engineer

- Reports
- QA
- Testing
- Documentation

---

# Project Success Criteria

The project will be considered successful when it can:

- Detect the correct product.
- Measure critical dimensions accurately.
- Identify missing features.
- Detect visible defects.
- Classify products as PASS or FAIL.
- Communicate with ESP32.
- Reject defective products automatically.
- Generate inspection logs.

---

# Risk Management

Potential risks include:

- Poor lighting conditions
- Camera calibration errors
- Insufficient dataset quality
- Hardware communication failures
- False detections
- Mechanical alignment issues

Mitigation strategies will be documented throughout the project.