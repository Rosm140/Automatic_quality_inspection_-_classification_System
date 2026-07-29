from pathlib import Path

from src.utils.file_manager import (
    ensure_directory,
    file_exists,
    timestamp_filename,
    save_json,
)

test_dir = Path("logs/test")
ensure_directory(test_dir)

filename = timestamp_filename("inspection", "json")

filepath = test_dir / filename

save_json({"status": "PASS"}, filepath)

print(file_exists(filepath))
print(filename)