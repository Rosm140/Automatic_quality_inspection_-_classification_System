
from src.utils.config_loader import load_config


def test_camera_config_loads():
    config = load_config("camera.yaml")

    assert config["camera"]["width"] == 1920
    assert config["camera"]["height"] == 1080
    assert config["camera"]["fps"] == 30
