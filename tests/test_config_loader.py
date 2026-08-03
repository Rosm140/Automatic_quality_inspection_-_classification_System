from src.utils.config_loader import load_config

config = load_config("camera.yaml")

print(config)
print(config["camera"]["width"])q
