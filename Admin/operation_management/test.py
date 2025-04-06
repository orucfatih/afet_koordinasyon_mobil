# api için test

from op_config import get_config

# Test için ana blok
if __name__ == "__main__":
    config = get_config()
    print("API Key:", config["api_key"])
    print("Default Center:", config["map_default_center"])
    print("Zoom:", config["map_default_zoom"])
    print("Debug Mode:", config["debug_mode"])