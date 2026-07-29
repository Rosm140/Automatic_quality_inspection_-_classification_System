from pathlib import Path
import yaml

from src.utils.constants import CONFIG_DIR


def load_config(filename: str) -> dict:
    """
    Load a YAML configuration file from the config directory.
    """

    config_path = CONFIG_DIR / filename

    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}"
        )

    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)