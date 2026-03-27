from dotenv import load_dotenv
from libs.system_info import get_hostname, Platform
import os, logging


def _getenv_bool(key, default=False):
    """Return the env var as a bool.

    Returns True only for the values 'true', '1', or 'yes' (case-insensitive).
    Any other value (including 'false', '0', 'no', empty string) returns False.
    If the env var is not set at all, *default* is returned.
    """
    val = os.getenv(key)
    if val is None:
        return default
    return val.strip().lower() in ("true", "1", "yes")


def _getenv_int(key, default):
    """Return the env var as an int, falling back to *default* on missing or invalid values."""
    val = os.getenv(key)
    if val is None:
        return default
    try:
        return int(val)
    except ValueError:
        logging.warning("Config: %s=%r is not a valid integer; using default %s", key, val, default)
        return default


class Parser(object):

    def __init__(self, config):
        load_dotenv(config)
        self.COMPUTER_NAME = os.getenv("COMPUTER_NAME", default=get_hostname())
        self.LOG_DIR = os.getenv("LOG_DIR", default="./logs")
        self.LOG_FILENAME = os.getenv("LOG_FILENAME", default="system2mqtt.log")
        self.OLD_LOG_FILENAME = os.getenv("OLD_LOG_FILENAME", default="old_system2mqtt.log")
        self.MQTT_BASE_TOPIC = os.getenv("MQTT_BASE_TOPIC", default="system2mqtt/{}".format(self.COMPUTER_NAME))
        self.PUBLISH_PERIOD = _getenv_int("PUBLISH_PERIOD", default=60)
        self.DEBUG_LOG = _getenv_bool("DEBUG_LOG", default=False)
        self.PROCPATH = os.getenv("PROCPATH", default="/proc")
        self.ARGON = _getenv_bool("ARGON", default=False)
        self.STORAGE_INCLUDE = os.getenv("STORAGE_INCLUDE", default=False)
        self.STORAGE_EXCLUDE = os.getenv("STORAGE_EXCLUDE", default=False)
        self.PVE_SYSTEM = _getenv_bool("PVE_SYSTEM", default=False)
        self.PVE_NODE_NAME = os.getenv("PVE_NODE_NAME", default="pve")
        self.PVE_HOST = os.getenv("PVE_HOST", default="localhost")
        self.PVE_USER = os.getenv("PVE_USER", default="root@pam")
        self.PVE_PASSWORD = os.getenv("PVE_PASSWORD")
        self.MQTT_HOST = os.getenv("MQTT_HOST", default="localhost")
        self.MQTT_PORT = _getenv_int("MQTT_PORT", default=1883)
        self.MQTT_USER = os.getenv("MQTT_USER", default=None)
        self.MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", default=None)
        self.MACOS = _getenv_bool("MACOS", default=False)
        self.CALLBACKS = os.getenv("CALLBACKS", default={})
        self.USER_CALLBACKS = _getenv_bool("USER_CALLBACKS", default=False)
        self.HA_DISCOVERY = _getenv_bool("HA_DISCOVERY", default=False)
        self.HA_DISCOVERY_BASE = os.getenv("HA_DISCOVERY_BASE", default="homeassistant")

        if Platform == "Darwin":
            self.MACOS = True
            self.PVE_SYSTEM = False
        else:
            self.MACOS = False

    def print_config(self):
        conf = "\n###############################################\n\nUsing Current Config\n\n"
        for k, v in self.__dict__.items():
            if "PASS".lower() in k.lower() or "PASSWORD".lower() in k.lower():
                if v:
                    v = '*' * len(str(v))
            conf += "{}: {}\n".format(k, v)
        conf += "\n###############################################\n\n"
        logging.info(conf)