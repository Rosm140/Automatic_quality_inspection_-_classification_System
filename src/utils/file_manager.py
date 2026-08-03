from pathlib import Path
from datetime import datetime
import json


def ensure_directory(path: Path) -> None:
    """Create a directory if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)


def file_exists(path: Path) -> bool:
    """Check if a file exists."""
    return path.exists()


def timestamp_filename(prefix: str, extension: str) -> str:
    """
    Example:
    inspection_20260729_223015.jpg
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"


def save_json(data: dict, filepath: Path) -> None:
    """Save a dictionary as JSON."""
    ensure_directory(filepath.parent)

    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)