from configparser import ConfigParser
from os import getlogin
from os.path import realpath, exists

# ---------- Default Values ----------
# Settings path
SETTINGS_FILE_NAME = "config.ini"
DISK = realpath(__file__)[0]
SETTINGS_PATH = SETTINGS_FILE_NAME

# Display
WIDTH = 1280
HEIGHT = 720


def load_settings():
    if not exists(SETTINGS_PATH):
        create_settings_file()
    config = ConfigParser()
    config.read(SETTINGS_PATH)
    return config


def create_settings_file():
    config = ConfigParser()
    config.read(SETTINGS_PATH)
    config.add_section("display")
    config.set("display", "width", str(WIDTH))
    config.set("display", "height", str(HEIGHT))

    with open('config.ini', 'w') as file:
        config.write(file)


def get_setting(section: str, key):
    config = ConfigParser()
    config.read(SETTINGS_PATH)
    return config.get(section, key)
