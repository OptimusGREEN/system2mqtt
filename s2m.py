#!/usr/bin/python3

# send all system info to mqtt

import logging, time, os, sys
from decimal import Decimal
from dotenv import load_dotenv

from libs.system_info import get_temps, Platform, get_hostname, get_disks, get_disk_space, get_memory, get_cpu
from libs.myqtt import Myqtt
from libs.optimox import OptiMOX, prox_auth


hostname = get_hostname()



############ ENV VARS #############
load_dotenv(sys.argv[1])

COMPUTER_NAME = os.getenv("COMPUTER_NAME", default=hostname)
LOG_DIR = os.getenv("LOG_DIR", default="./logs")
LOG_FILENAME = os.getenv("LOG_FILENAME", default="system2mqtt.log")
OLD_LOG_FILENAME = os.getenv("OLD_LOG_FILENAME", default="old_system2mqtt.log")
MQTT_BASE_TOPIC = os.getenv("MQTT_BASE_TOPIC", default="system2mqtt/{}".format(COMPUTER_NAME))
PUBLISH_PERIOD = os.getenv("PUBLISH_PERIOD", default=30)
DEBUG_LOG = os.getenv("DEBUG_LOG", default=False)

PVE_SYSTEM = os.getenv("PVE_SYSTEM", default=False)
PVE_NODE_NAME = os.getenv("PVE_NODE_NAME", default="pve")
PVE_HOST = os.getenv("PVE_HOST", default="localhost")
PVE_USER = os.getenv("PVE_USER", default="root@pam")
PVE_PASSWORD = os.getenv("PVE_PASSWORD")

MQTT_HOST = os.getenv("MQTT_HOST", default="localhost")
MQTT_PORT = os.getenv("MQTT_PORT", default=1883)
MQTT_USER = os.getenv("MQTT_USER", default=None)
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", default=None)

###################################

if Platform == "Darwin":
    macos = True
    PVE_SYSTEM = False
else:
    macos = False

lwt_topic = MQTT_BASE_TOPIC + "/LWT"


def setupLogging(DEBUG_MODE=False):
    log_dir = LOG_DIR
    log_filename = os.path.join(log_dir, LOG_FILENAME)
    old_log_filename = os.path.join(log_dir, OLD_LOG_FILENAME)
    os.makedirs(log_dir, exist_ok=True)
    if os.path.exists(log_filename):
        if os.path.exists(old_log_filename):
            try: os.remove(old_log_filename)
            except: print("Couldn't remove old log")
        os.rename(log_filename, old_log_filename)
    if DEBUG_MODE:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    format = "OptiSERVE [%(levelname)s] [%(module)s:%(lineno)d] " + " - %(asctime)s - %(message)s"
    if DEBUG_MODE:
        logging.basicConfig(level=log_level,format=format,handlers=[logging.FileHandler(log_filename),logging.StreamHandler()])
    else:
        logging.basicConfig(filename=log_filename, level=log_level, format=format)

setupLogging(DEBUG_LOG)


################################################################################################

class System2Mqtt(object):

    def __init__(self):
        logging.debug("")

        self.myqtt = Myqtt(host=MQTT_HOST,
                            port=MQTT_PORT,
                            username=MQTT_USER,
                            password=MQTT_PASSWORD)

        self.myqtt.lwt_topic = lwt_topic
        self.myqtt.topic_callbacks = self.__get_subscription_calbacks()

        if PVE_SYSTEM:
            self.pve = OptiMOX(prox_auth(PVE_HOST,
                                        PVE_USER,
                                        PVE_PASSWORD))

        self.auto_reconnect = True

        self.mounted_disks = []

    def __get_subscription_calbacks(self):
        logging.debug("")
        sub_dict = {MQTT_BASE_TOPIC + "/tele/PUBLISH_PERIOD": self.s2m_set_publish_period,
                    MQTT_BASE_TOPIC + "/callbacks/s2m_quit": self.quit_s2m}
        return sub_dict

    def run(self):
        logging.debug("")
        self.myqtt.run()
        self.wait()

    def wait(self):
        logging.debug("...")
        while not self.myqtt.client.is_connected():
            logging.debug("Trying to connect...")
            time.sleep(2)
        self.start_publish_loop()

    def start_publish_loop(self):
        logging.info("Publish period is set to {} seconds.".format(PUBLISH_PERIOD))
        while self.myqtt.client.is_connected():
            logging.debug("flag: {}".format(self.myqtt.connected_flag))
            self.publish_all()
            time.sleep(int(PUBLISH_PERIOD))
        if self.auto_reconnect:
            logging.info("Reconnecting...")
            self.wait()
            self.myqtt.client.reconnect()
        logging.warning("Main Loop Ended!")

    def publish_mount_state(self):
        logging.debug("")
        base = MQTT_BASE_TOPIC + "/disks/mount/"
        try:
            if not PVE_SYSTEM:
                disks = get_disks('internal')
                for d in disks:
                    if d == "/":
                        label = "root"
                    else:
                        label = d.split("/")[-1]
                    final_topic = base + label
                    logging.info("{} is mounted - publishing to '{}'".format(label, final_topic))
                    self.myqtt.publish(final_topic, "mounted")
            elif PVE_SYSTEM:
                storage_data = self.pve.getNodeStorage(PVE_NODE_NAME)["data"]
                for storage in storage_data:
                    name = storage["storage"]
                    state = storage["active"]
                    final_topic = base + name
                    logging.info("Storage: {}: {}%".format(name, state))
                    self.myqtt.publish(final_topic, state)
            else:
                logging.warning("Hmm, something went wrong")
        except Exception as e:
            logging.error(e)

    def publish_disk_space(self):
        logging.debug("")
        base = MQTT_BASE_TOPIC + "/disks/storage/"
        try:
            if not PVE_SYSTEM:
                disks = get_disks()
                for d in disks:
                    space = get_disk_space(d)
                    if d == "/":
                        label = "root"
                    else:
                        label = d.split("/")[-1]
                    final_topic = base + label
                    self.myqtt.publish(final_topic, space)
            elif PVE_SYSTEM:
                storage_data = self.pve.getNodeStorage(PVE_NODE_NAME)["data"]
                logging.debug(storage_data)
                for storage in storage_data:
                    name = storage["storage"]
                    pct = int(float(storage["used_fraction"]) * 100)
                    final_topic = base + name
                    logging.info("Storage: {}: {}%".format(name, pct))
                    self.myqtt.publish(final_topic, pct)
            else:
                logging.warning("Hmm, something went wrong")
        except Exception as e:
            logging.error(e)

    def publish_cpu_temp(self):
        logging.debug("")
        final_topic = MQTT_BASE_TOPIC + "/cpu/temperature"
        try:
            if macos:
                try:
                    dec = Decimal(get_temps())
                    temp = str(round(dec, 1))
                except Exception as e:
                    logging.warning(e)
                    temp = get_temps()
                logging.info("CPU temperature: {}°C".format(temp))
                self.myqtt.publish(final_topic, temp)
            else:
                try:
                    temps = get_temps()["coretemp"]
                except:
                    temps = get_temps()["cpu_thermal"]
                c_list = []
                for temp in temps:
                    c_list.append(temp.current)
                highest = max(c_list)
                logging.info("CPU temperature: {}°C".format(highest))
                self.myqtt.publish(final_topic, str(highest))
        except Exception as e:
            logging.error(e)

    def publish_cpu_usage(self):
        logging.debug("")
        final_topic = MQTT_BASE_TOPIC + "/cpu/usage"
        try:
            if not PVE_SYSTEM:
                cpu = get_cpu()
                logging.info("CPU usage: {}%".format(cpu))
                self.myqtt.publish(final_topic, cpu)
            elif PVE_SYSTEM:
                cpu = self.pve.getNodeStatus(PVE_NODE_NAME)["data"]["cpu"]
                pct = int(float(cpu) * 100)
                logging.info("CPU usage: {}%".format(pct))
                if pct > 0:
                    self.myqtt.publish(final_topic, pct)
            else:
                logging.warning("Hmm, something went wrong")
        except Exception as e:
            logging.error(e)

    def publish_ram(self):
        logging.debug("")
        final_topic = MQTT_BASE_TOPIC + "/memory"
        try:
            if not PVE_SYSTEM:
                mem = get_memory()
                logging.info("Memory Used: {}%".format(mem))
                self.myqtt.publish(final_topic, mem)
            elif PVE_SYSTEM:
                ram_dict = self.pve.getNodeStatus(PVE_NODE_NAME)["data"]["memory"]
                used = float(ram_dict["used"])
                total = float(ram_dict["total"])
                pct = int((used / total) * 100)
                logging.info("Ram usage: {}%".format(pct))
                self.myqtt.publish(final_topic, pct)
            else:
                logging.warning("Not MacOS or PVE system")
        except Exception as e:
            logging.error(e)

    def publish_all(self):
        logging.debug("...publishing")
        self.myqtt.publish(lwt_topic, 'online')
        funcs = [self.publish_mount_state,
                 self.publish_disk_space,
                 self.publish_cpu_temp,
                 self.publish_cpu_usage,
                 self.publish_ram]
        for f in funcs:
            f()


################################################################################################
################################       CALLBACKS      ##########################################
################################################################################################


    def s2m_set_publish_period(self, client, userdata, message):
        logging.debug("")
        global PUBLISH_PERIOD
        try:
            new_publish_period = int(message.payload.decode("utf-8"))
            if new_publish_period != PUBLISH_PERIOD:
                PUBLISH_PERIOD = new_publish_period
                logging.info("Publish period has been set to {} seconds.".format(PUBLISH_PERIOD))
        except Exception as e:
            logging.error(e)
            PUBLISH_PERIOD = 30

    def quit_s2m(self, client, userdata, message):
        logging.debug("")
        if int(message.payload.decode("utf-8")) == 1:
            self.auto_reconnect =False
            logging.info("Quit called....")
            self.myqtt.publish(MQTT_BASE_TOPIC + "/callbacks/s2m_quit", "")
            self.myqtt.publish(lwt_topic, "exited", retain=True)
            client.loop_stop()
            client.disconnect()




if __name__ == '__main__':
    s2m = System2Mqtt()
    s2m.run()
