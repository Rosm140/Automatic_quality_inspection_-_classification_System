"""
Project-wide constants.
Do not hardcode values elsewhere in the project.
"""

from pathlib import Path

# --------------------------------------------------
# Project Information
# --------------------------------------------------

PROJECT_NAME = "Automatic Quality Inspection System"
PROJECT_VERSION = "1.0.0"

# --------------------------------------------------
# Paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
LOG_DIR = PROJECT_ROOT / "logs"
MODEL_DIR = PROJECT_ROOT / "models"
DOCS_DIR = PROJECT_ROOT / "docs"
TEST_DIR = PROJECT_ROOT / "tests"

# --------------------------------------------------
# Camera
# --------------------------------------------------

DEFAULT_CAMERA_ID = 0

DEFAULT_WIDTH = 1920
DEFAULT_HEIGHT = 1080

# --------------------------------------------------
# Image Formats
# --------------------------------------------------

IMAGE_EXTENSION = ".png"

SUPPORTED_IMAGE_FORMATS = (
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
)

# --------------------------------------------------
# Logging
# --------------------------------------------------

DEFAULT_LOG_LEVEL = "INFO"

SYSTEM_LOG_FILE = LOG_DIR / "system.log"

# --------------------------------------------------
# Serial Communication
# --------------------------------------------------

DEFAULT_BAUD_RATE = 115200

DEFAULT_SERIAL_TIMEOUT = 1