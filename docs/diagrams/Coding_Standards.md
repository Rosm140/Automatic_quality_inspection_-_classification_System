# Coding Standards

## Purpose

This document defines the coding standards, project conventions, Git workflow, and review process for the AI-Based Visual & Dimensional Quality Inspection System.

Every team member must follow these standards.

---

# Project Structure

```
project/

config/
data/
models/
src/
tests/
arduino/
docs/
logs/
assets/

README.md
requirements.txt
.gitignore
```

---

# Python Coding Style

We follow **PEP 8**.

### Maximum line length

88 Characters

---

### Indentation

Use

- 4 Spaces

Never use tabs.

---

### Naming Convention

## Variables

```python
image_path
product_width
camera_matrix
```

---

## Functions

```python
capture_image()

measure_diameter()

detect_product()

calculate_area()
```

snake_case only.

---

## Classes

```python
CameraManager

MeasurementEngine

DecisionEngine

ESP32Controller
```

PascalCase only.

---

## Constants

```python
MAX_PRODUCTS

CAMERA_WIDTH

SERIAL_PORT
```

UPPER_CASE only.

---

# Folder Responsibility

## config/

Configuration files

---

## data/

Datasets

Calibration

Images

---

## models/

YOLO weights

Future AI models

---

## src/

Python source code

---

## tests/

Unit testing

---

## arduino/

ESP32 programs

---

## docs/

Project documentation

---

## logs/

Inspection logs

---

# Module Naming

Good

```
camera.py

measurement.py

inspection.py

communication.py

decision_engine.py
```

Bad

```
abc.py

test1.py

new.py

python.py
```

---

# Function Rules

Every function should perform **one responsibility only**.

Good

```python
capture_image()

detect_product()

measure_width()
```

Bad

```python
capture_detect_measure_save_everything()
```

---

# Documentation

Every function must include a docstring.

Example

```python
def capture_image():
    """
    Capture an image from the Sony IMX335 camera.

    Returns:
        numpy.ndarray: Captured image frame.
    """
```

---

# Comments

Write comments only when they explain *why*, not *what*.

Good

```python
# Apply Gaussian Blur to reduce sensor noise
```

Bad

```python
# Create image variable
image = ...
```

---

# Git Workflow

Only the Team Leader can merge into `main`.

Team members work on feature branches.

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

Sprint1-Day2-Camera

Sprint2-Day3-YOLO

Sprint3-Day2-Measurement
```

Avoid vague messages like:

```
update

fixed

changes

new
```

---

# Pull Request Checklist

Before creating a Pull Request:

- Code runs without errors.
- No unnecessary files added.
- Documentation updated (if required).
- Proper commit message used.
- Tested locally.

---

# Code Review Checklist

The Team Leader should verify:

- Code readability
- Naming conventions
- Logic correctness
- Performance
- Documentation
- No duplicate code

---

# Error Handling

Never silently ignore errors.

Good

```python
try:
    camera.open()
except Exception as e:
    print(e)
```

Bad

```python
try:
    camera.open()
except:
    pass
```

---

# Testing

Every major module should be tested independently before integration.

Examples:

- Camera
- YOLO
- Measurement
- ESP32
- Servo

---

# Documentation Rules

Every completed feature should include:

- Description
- Input
- Output
- Dependencies
- Known limitations

---

# Development Philosophy

The project should be:

- Modular
- Readable
- Maintainable
- Reusable
- Scalable

Avoid shortcuts that make future maintenance difficult.

---

# Team Rule

Before pushing code:

1. Test it.
2. Review it.
3. Commit it.
4. Push it.
5. Create a Pull Request.

Quality is more important than speed, but with good planning we aim to achieve both.