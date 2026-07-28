# ESP32 Wiring Documentation

## ESP32 Board

ESP32 DevKit V1

---

# Pin Connections

| Component | ESP32 Pin | Function |
|-----------|-----------|----------|
| Servo Signal | GPIO18 | Servo PWM Control |
| Servo VCC | 5V | Servo Power |
| Servo GND | GND | Common Ground |
| IR Sensor OUT | GPIO4 | Object Detection |
| IR Sensor VCC | 3.3V | Sensor Power |
| IR Sensor GND | GND | Ground |
| USB | USB Port | Programming & Communication |

---

# Servo Motor Wiring

Servo Wire Colors

Brown → GND

Red → 5V

Orange → GPIO18

---

# IR Sensor Wiring

VCC → 3.3V

GND → GND

OUT → GPIO4

---

# USB Connection

ESP32 connects to the laptop using a USB cable.

Purpose:

- Upload firmware
- Serial communication
- Debugging
- Power during development

---

# Laptop Communication

Communication Protocol:

Serial over USB

Baud Rate:

115200 bps

Development Software:

Arduino IDE

Data Flow:

Laptop
↓

USB

↓

ESP32

↓

Servo / IR Sensor

---

# Wiring Notes

- Use a common ground for all components.
- Use an external 5V supply for the servo if required to avoid voltage drops.
- Keep wiring short and secure.
- Verify connections before powering the system.