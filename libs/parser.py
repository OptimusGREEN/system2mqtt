from dotenv import load_dotenv
from libs.system_info import get_hostname, Platform
import os, logging


class Parser(object):

    def __init__(self, config):
        load_dotenv(config)
        self.COMPUTER_NAME = os.getenv("COMPUTER_NAME", default=get_hostname())
        self.LOG_DIR = os.getenv("LOG_DIR", default="./logs")
        self.LOG_FILENAME = os.getenv("LOG_FILENAME", default="system2mqtt.log")
        self.OLD_LOG_FILENAME = os.getenv("OLD_LOG_FILENAME", default="old_system2mqtt.log")
        self.MQTT_BASE_TOPIC = os.getenv("MQTT_BASE_TOPIC", default="system2mqtt/{}".format(self.COMPUTER_NAME))
        self.PUBLISH_PERIOD = os.getenv("PUBLISH_PERIOD", default=60)
        self.DEBUG_LOG = os.getenv("DEBUG_LOG", default=False)
        self.PROCPATH = os.getenv("PROCPATH", default="/proc")
        self.ARGON = os.getenv("ARGON", default=False)
        self.STORAGE_INCLUDE = os.getenv("STORAGE_INCLUDE", default=False)
        self.STORAGE_EXCLUDE = os.getenv("STORAGE_EXCLUDE", default=False)
        self.PVE_SYSTEM = os.getenv("PVE_SYSTEM", default=False)
        self.PVE_NODE_NAME = os.getenv("PVE_NODE_NAME", default="pve")
        self.PVE_HOST = os.getenv("PVE_HOST", default="localhost")
        self.PVE_USER = os.getenv("PVE_USER", default="root@pam")
        self.PVE_PASSWORD = os.getenv("PVE_PASSWORD")
        self.MQTT_HOST = os.getenv("MQTT_HOST", default="localhost")
        self.MQTT_PORT = os.getenv("MQTT_PORT", default=1883)
        self.MQTT_USER = os.getenv("MQTT_USER", default=None)
        self.MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", default=None)
        self.MACOS = os.getenv("MACOS", default=False)
        self.CALLBACKS = os.getenv("CALLBACKS", default={})
        self.USER_CALLBACKS = os.getenv("USER_CALLBACKS", default=False)
        self.HA_DISCOVERY = os.getenv("HA_DISCOVERY", default=False)
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