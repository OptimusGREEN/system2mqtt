#!/usr/bin/env python3

# send all system info to mqtt

import logging, time, os, sys, ast
from decimal import Decimal
from subprocess import check_call

from libs.system_info import get_temps, Platform, get_hostname, get_disks, get_disk_space, get_memory, get_cpu, set_proc, get_argon_fan_speed
from libs.myqtt import Myqtt
from libs.optimox import OptiMOX, prox_auth
from libs.parser import Parser
from libs.argon import gethddtemp
from libs.homeassistant import ha_config

hostname = get_hostname()



def setupLogging(DEBUG_MODE=False, conf=None):
    config = conf
    title = config.COMPUTER_NAME.upper()
    log_dir = config.LOG_DIR
    if log_dir.startswith("./"):
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), log_dir.split("./")[1])
    print("Log Dir: ", log_dir)
    log_filename = os.path.join(log_dir, config.LOG_FILENAME)
    old_log_filename = os.path.join(log_dir, config.OLD_LOG_FILENAME)
    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception as e:
        print(e)
    if os.path.exists(log_filename):
        if os.path.exists(old_log_filename):
            try: os.remove(old_log_filename)
            except: print("Couldn't remove old log")
        os.rename(log_filename, old_log_filename)
    if DEBUG_MODE:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    format = "{}: [%(levelname)s] [%(module)s:%(lineno)d] ".format(title) + " - %(asctime)s - %(message)s"
    if DEBUG_MODE:
        logging.basicConfig(level=log_level,format=format,handlers=[logging.FileHandler(log_filename),logging.StreamHandler()])
    else:
        logging.basicConfig(filename=log_filename, level=log_level, format=format)


################################################################################################

class System2Mqtt(object):

    def __init__(self, conf):

        print("Getting config from:\n", conf)

        self.config = Parser(conf)
        setupLogging(self.config.DEBUG_LOG, self.config)
        logging.debug("logging has been set up")
        self.lwt_topic = self.config.MQTT_BASE_TOPIC + "/LWT"
        self.availability_topic = self.lwt_topic

        self.myqtt = Myqtt(host=self.config.MQTT_HOST,
                            port=self.config.MQTT_PORT,
                            username=self.config.MQTT_USER,
                            password=self.config.MQTT_PASSWORD)

        self.myqtt.lwt_topic = self.lwt_topic
        self.myqtt.topic_callbacks = self.__get_subscription_calbacks()

        if self.config.PVE_SYSTEM:
            self.pve = OptiMOX(prox_auth(self.config.PVE_HOST,
                                        self.config.PVE_USER,
                                        self.config.PVE_PASSWORD))

        self.auto_reconnect = True

        self.mounted_disks = []

        self.ha_discovery_template = "{}/{}/{}/config".format(self.config.HA_DISCOVERY_BASE, "{}", "{}")

        self.publish_period = self.config.PUBLISH_PERIOD

        self.first_loop_done = False

    def __get_subscription_calbacks(self):
        logging.debug("")
        sub_dict = {self.config.MQTT_BASE_TOPIC + "/tele/PUBLISH_PERIOD": self.s2m_set_publish_period,
                    self.config.MQTT_BASE_TOPIC + "/callbacks/s2m_quit": self.quit_s2m,
                    self.config.MQTT_BASE_TOPIC + "/callbacks/shutdown": self.cb_shutdown,
                    self.config.MQTT_BASE_TOPIC + "/callbacks/reboot": self.cb_reboot}
        return sub_dict

    def run(self):
        self.config.print_config()
        try:
            self.process_user_callbacks()
        except Exception as e:
            logging.error(e, exc_info=True)
        self.myqtt.run()
        self.wait()

    def wait(self):
        logging.debug("...")
        while not self.myqtt.client.is_connected():
            logging.debug("Trying to connect...")
            time.sleep(2)
        self.start_publish_loop()

    def start_publish_loop(self):
        logging.info("Publish period is set to {} seconds.".format(self.publish_period))
        while self.myqtt.client.is_connected():
            logging.debug("mqtt flag: {}".format(self.myqtt.connected_flag))
            self.publish_all()
            time.sleep(int(self.publish_period))
        if self.auto_reconnect:
            logging.info("Reconnecting...")
            self.wait()
            self.myqtt.client.reconnect()
        logging.warning("Main Loop Ended!")

    def publish_mount_state(self):
        logging.debug("")
        ha_type = "binary_sensor"
        ha_class = "connectivity"
        slug = "/disks/mount/"
        base = self.config.MQTT_BASE_TOPIC + slug
        try:
            if not self.config.PVE_SYSTEM:
                disks = get_disks(procpath=self.config.PROCPATH)
                for d in disks:
                    if d == "/":
                        label = "sysroot"
                    else:
                        label = d.split("/")[-1]
                    final_topic = base + label
                    logging.debug("\nlabel: {}\n".format(label))
                    if self.config.STORAGE_INCLUDE:
                        include = ast.literal_eval(self.config.STORAGE_INCLUDE.lower())
                        if label.lower() in include:
                            logging.debug("...included")
                            pass
                        else:
                            logging.debug("...ignoring")
                            continue
                    else:
                        if self.config.STORAGE_EXCLUDE:
                            exclude = ast.literal_eval(self.config.STORAGE_EXCLUDE.lower())
                            if not label.lower() in exclude:
                                pass
                            else:
                                continue
                    logging.info("{} is mounted - publishing to '{}'".format(label, final_topic))
                    self.myqtt.publish(final_topic, "mounted")
                    if self.config.HA_DISCOVERY and not self.first_loop_done:
                        title = label
                        for char in (" ", "-"):
                            label = label.lower().replace(char, "_")
                        device = self.config.COMPUTER_NAME
                        logging.debug("device: {}".format(device))
                        for char in (" ", "-"):
                            device = device.replace(char, "_")
                        ha_object_id = "s2m_"+device+"_{}_{}".format(label, "mounted")
                        logging.debug("object_id: {}".format(ha_object_id))
                        ha_name = "{} Mount State".format(title).title()
                        logging.debug("ha_name: {}".format(ha_name))
                        logging.debug("ha_type: {}".format(ha_type))
                        dtt = self.ha_discovery_template.format(ha_type, ha_object_id)
                        logging.debug("dtt: {}".format(dtt))
                        haconfig = ha_config(discovery_topic=dtt, name=ha_name, object_id=ha_object_id,
                                             state_topic=final_topic, device=device, payload_on="mounted",
                                             off_delay=int(self.publish_period)+10, entity_type=ha_type, device_class=ha_class, 
                                             availability_topic=self.availability_topic, 
                                             payload_available="online",
                                             payload_not_available="offline")
                        self.myqtt.publish(haconfig[0], haconfig[1], retain=False)
                        logging.debug("T: {}".format(haconfig[0]))
                        logging.debug("P: {}".format(haconfig[1]))
                    else:
                        logging.debug("HA Discovery not being sent")
            elif self.config.PVE_SYSTEM:
                storage_data = self.pve.getNodeStorage(self.config.PVE_NODE_NAME)["data"]
                for storage in storage_data:
                    label = storage["storage"]
                    state = storage["active"]
                    final_topic = base + label
                    if self.config.STORAGE_INCLUDE:
                        include = ast.literal_eval(self.config.STORAGE_INCLUDE.lower())
                        if label.lower() in include:
                            pass
                        else:
                            continue
                    else:
                        if self.config.STORAGE_EXCLUDE:
                            exclude = ast.literal_eval(self.config.STORAGE_EXCLUDE.lower())
                            if not label.lower() in exclude:
                                pass
                            else:
                                continue
                    logging.info("Storage: {}: {}%".format(label, state))
                    self.myqtt.publish(final_topic, state)
                    if self.config.HA_DISCOVERY and not self.first_loop_done:
                        title = label
                        for char in (" ", "-"):
                            label = label.lower().replace(char, "_")
                        device = self.config.COMPUTER_NAME
                        for char in (" ", "-"):
                            device = device.replace(char, "_")
                        ha_object_id = "s2m_"+device+"_{}_{}".format(label, "mounted")
                        ha_name = "{} Mount State".format(title).title()
                        dtt = self.ha_discovery_template.format(ha_type, ha_object_id)
                        haconfig = ha_config(discovery_topic=dtt, name=ha_name, object_id=ha_object_id,
                                             entity_type = ha_type, device_class = ha_class,
                                             state_topic=final_topic, device=device, payload_on=1, payload_off=0, 
                                             availability_topic=self.availability_topic, 
                                             payload_available="online",
                                             payload_not_available="offline")
                        self.myqtt.publish(haconfig[0], haconfig[1], retain=True)
            else:
                logging.warning("Hmm, something went wrong")
        except Exception as e:
            logging.error(e, exc_info=True)

    def publish_disk_space(self):
        logging.debug("")
        ha_type = "sensor"
        ha_icon = "mdi:harddisk"
        ha_unit = "%"
        slug = "/disks/storage/"
        base = self.config.MQTT_BASE_TOPIC + slug
        try:
            if not self.config.PVE_SYSTEM:
                disks = get_disks(procpath=self.config.PROCPATH)
                for d in disks:
                    # space = get_disk_space(d, procpath=self.config.PROCPATH)
                    if d == "/":
                        label = "sysroot"
                    else:
                        label = d.split("/")[-1]
                    if self.config.STORAGE_INCLUDE:
                        include = ast.literal_eval(self.config.STORAGE_INCLUDE.lower())
                        print(include)
                        print(type(include))
                        if label.lower() in include:
                            pass
                        else:
                            continue
                    else:
                        if self.config.STORAGE_EXCLUDE:
                            exclude = ast.literal_eval(self.config.STORAGE_EXCLUDE.lower())
                            if not label.lower() in exclude:
                                pass
                            else:
                                continue
                    space = get_disk_space(d, procpath=self.config.PROCPATH)
                    final_topic = base + label
                    self.myqtt.publish(final_topic, space)
                    if self.config.HA_DISCOVERY and not self.first_loop_done:
                        title = label
                        for char in (" ", "-"):
                            label = label.lower().replace(char, "_")
                        device = self.config.COMPUTER_NAME
                        for char in (" ", "-"):
                            device = device.replace(char, "_")
                        ha_object_id = "s2m_"+device+"_{}_{}".format(label, "storage")
                        ha_name = "{} Storage".format(title).title()
                        dtt = self.ha_discovery_template.format(ha_type, ha_object_id)
                        haconfig = ha_config(discovery_topic=dtt, name=ha_name, object_id=ha_object_id, state_topic=final_topic,
                                             device=device, icon=ha_icon, entity_type=ha_type, unit=ha_unit, 
                                             availability_topic=self.availability_topic, 
                                             payload_available="online",
                                             payload_not_available="offline")
                        self.myqtt.publish(haconfig[0], haconfig[1], retain=True)
            elif self.config.PVE_SYSTEM:
                storage_data = self.pve.getNodeStorage(self.config.PVE_NODE_NAME)["data"]
                logging.debug(storage_data)
                for storage in storage_data:
                    label = storage["storage"]
                    pct = int(float(storage["used_fraction"]) * 100)
                    final_topic = base + label
                    if self.config.STORAGE_INCLUDE:
                        include = ast.literal_eval(self.config.STORAGE_INCLUDE.lower())
                        if label.lower() in include:
                            pass
                        else:
                            continue
                    else:
                        if self.config.STORAGE_EXCLUDE:
                            exclude = ast.literal_eval(self.config.STORAGE_EXCLUDE.lower())
                            if not label.lower() in exclude:
                                pass
                            else:
                                continue
                    logging.info("Storage: {}: {}%".format(label, pct))
                    self.myqtt.publish(final_topic, pct)
                    if self.config.HA_DISCOVERY and not self.first_loop_done:
                        title = label
                        for char in (" ", "-"):
                            label = label.lower().replace(char, "_")
                        device = self.config.COMPUTER_NAME
                        for char in (" ", "-"):
                            device = device.replace(char, "_")
                        ha_object_id = "s2m_"+device+"_{}_{}".format(label, "storage")
                        ha_name = "{} Storage".format(title).title()
                        dtt = self.ha_discovery_template.format(ha_type, ha_object_id)
                        haconfig = ha_config(discovery_topic=dtt, name=ha_name, object_id=ha_object_id, state_topic=final_topic,
                                             device=device, icon=ha_icon, entity_type=ha_type, unit=ha_unit, 
                                             availability_topic=self.availability_topic, 
                                             payload_available="online",
                                             payload_not_available="offline")
                        self.myqtt.publish(haconfig[0], haconfig[1], retain=True)
            else:
                logging.warning("Hmm, something went wrong")
        except Exception as e:
            logging.error(e, exc_info=True)

    def publish_cpu_temp(self):
        logging.debug("")
        ha_type = "sensor"
        ha_class = "temperature"
        # ha_icon = "mdi:thermometer"
        ha_unit = "°C"
        slug = "/cpu/temperature"
        final_topic = self.config.MQTT_BASE_TOPIC + slug
        try:
            if self.config.MACOS:
                try:
                    dec = Decimal(get_temps(procpath=self.config.PROCPATH))
                    temp = str(round(dec, 1))
                except Exception as e:
                    logging.warning(e)
                    temp = get_temps(procpath=self.config.PROCPATH)
                logging.info("CPU temperature: {}°C".format(temp))
                self.myqtt.publish(final_topic, temp)
                if self.config.HA_DISCOVERY and not self.first_loop_done:
                    title = self.config.COMPUTER_NAME + " CPU Temperature"
                    device = self.config.COMPUTER_NAME
                    for char in (" ", "-"):
                        device = device.replace(char, "_")
                    ha_object_id = "s2m_" + device + "_{}".format("cpu_temperature")
                    ha_name = title.title()
                    dtt = self.ha_discovery_template.format(ha_type, ha_object_id)
                    haconfig = ha_config(discovery_topic=dtt, name=ha_name, object_id=ha_object_id, state_topic=final_topic,
                                         device=device, entity_type=ha_type, unit=ha_unit, device_class=ha_class, 
                                         availability_topic=self.availability_topic, 
                                         payload_available="online",
                                         payload_not_available="offline")
                    self.myqtt.publish(haconfig[0], haconfig[1], retain=False)
            else:
                try:
                    temps = get_temps(procpath=self.config.PROCPATH)["coretemp"]
                except:
                    temps = get_temps(procpath=self.config.PROCPATH)["cpu_thermal"]
                c_list = []
                for temp in temps:
                    c_list.append(temp.current)
                highest = max(c_list)
                logging.info("CPU temperature: {}°C".format(highest))
                self.myqtt.publish(final_topic, str(highest))
                if self.config.HA_DISCOVERY and not self.first_loop_done:
                    title = self.config.COMPUTER_NAME + " CPU Temperature"
                    device = self.config.COMPUTER_NAME
                    for char in (" ", "-"):
                        device = device.replace(char, "_")
                    ha_object_id = "s2m_" + device + "_{}".format("cpu_temperature")
                    ha_name = title.title()
                    dtt = self.ha_discovery_template.format(ha_type, ha_object_id)
                    haconfig = ha_config(discovery_topic=dtt, name=ha_name, object_id=ha_object_id, state_topic=final_topic,
                                         device=device, entity_type=ha_type, unit=ha_unit, device_class=ha_class, 
                                         availability_topic=self.availability_topic, 
                                         payload_available="online",
                                         payload_not_available="offline")
                    self.myqtt.publish(haconfig[0], haconfig[1], retain=False)
        except Exception as e:
            logging.error(e, exc_info=True)

    def publish_cpu_usage(self):
        logging.debug("")
        ha_type = "sensor"
        ha_unit = "%"
        ha_icon = "mdi:cpu-64-bit"
        slug = "/cpu/usage"
        final_topic = self.config.MQTT_BASE_TOPIC + slug
        try:
            if not self.config.PVE_SYSTEM:
                cpu = get_cpu(procpath=self.config.PROCPATH)
                logging.info("CPU usage: {}%".format(cpu))
                self.myqtt.publish(final_topic, cpu)
                if self.config.HA_DISCOVERY and not self.first_loop_done:
                    title = self.config.COMPUTER_NAME + " CPU Usage"
                    device = self.config.COMPUTER_NAME
                    for char in (" ", "-"):
                        device = device.replace(char, "_")
                    ha_object_id = "s2m_" + device + "_{}".format("cpu")
                    ha_name = title.title()
                    dtt = self.ha_discovery_template.format(ha_type, ha_object_id)
                    haconfig = ha_config(discovery_topic=dtt, name=ha_name, object_id=ha_object_id, state_topic=final_topic,
                                         device=device, icon=ha_icon, entity_type=ha_type, unit=ha_unit, 
                                         availability_topic=self.availability_topic, 
                                         payload_available="online",
                                         payload_not_available="offline")
                    self.myqtt.publish(haconfig[0], haconfig[1], retain=False)
            elif self.config.PVE_SYSTEM:
                cpu = self.pve.getNodeStatus(self.config.PVE_NODE_NAME)["data"]["cpu"]
                pct = int(float(cpu) * 100)
                logging.info("CPU usage: {}%".format(pct))
                if pct > 0:
                    self.myqtt.publish(final_topic, pct)
                    if self.config.HA_DISCOVERY and not self.first_loop_done:
                        title = self.config.COMPUTER_NAME + " CPU Usage"
                        device = self.config.COMPUTER_NAME
                        for char in (" ", "-"):
                            device = device.replace(char, "_")
                        ha_object_id = "s2m_" + device + "_{}".format("cpu")
                        ha_name = title.title()
                        dtt = self.ha_discovery_template.format(ha_type, ha_object_id)
                        haconfig = ha_config(discovery_topic=dtt, name=ha_name, object_id=ha_object_id, state_topic=final_topic,
                                             device=device, icon=ha_icon, entity_type=ha_type, unit=ha_unit, 
                                             availability_topic=self.availability_topic, 
                                             payload_available="online",
                                             payload_not_available="offline")
                        self.myqtt.publish(haconfig[0], haconfig[1], retain=False)
            else:
                logging.warning("Hmm, something went wrong")
        except Exception as e:
            logging.error(e, exc_info=True)

    def publish_ram(self):
        logging.debug("Getting ram")
        ha_type = "sensor"
        ha_unit = "%"
        ha_icon = "mdi:memory"
        slug = "/memory"
        final_topic = self.config.MQTT_BASE_TOPIC + slug
        try:
            if not self.config.PVE_SYSTEM:
                mem = get_memory(procpath=self.config.PROCPATH)
                logging.info("Memory Used: {}%".format(mem))
                self.myqtt.publish(final_topic, mem)
                if self.config.HA_DISCOVERY and not self.first_loop_done:
                    title = self.config.COMPUTER_NAME + " Memory Usage"
                    device = self.config.COMPUTER_NAME
                    for char in (" ", "-"):
                        device = device.replace(char, "_")
                    ha_object_id = "s2m_" + device + "_{}".format("memory")
                    ha_name = title.title()
                    dtt = self.ha_discovery_template.format(ha_type, ha_object_id)
                    haconfig = ha_config(discovery_topic=dtt, name=ha_name, object_id=ha_object_id, state_topic=final_topic,
                                         device=device, icon=ha_icon, entity_type=ha_type, unit=ha_unit, 
                                         availability_topic=self.availability_topic, 
                                         payload_available="online",
                                         payload_not_available="offline")
                    self.myqtt.publish(haconfig[0], haconfig[1], retain=False)
            elif self.config.PVE_SYSTEM:
                ram_dict = self.pve.getNodeStatus(self.config.PVE_NODE_NAME)["data"]["memory"]
                used = float(ram_dict["used"])
                total = float(ram_dict["total"])
                pct = int((used / total) * 100)
                logging.info("Ram usage: {}%".format(pct))
                self.myqtt.publish(final_topic, pct)
                if self.config.HA_DISCOVERY and not self.first_loop_done:
                    title = self.config.COMPUTER_NAME + " Memory Usage"
                    device = self.config.COMPUTER_NAME
                    for char in (" ", "-"):
                        device = device.replace(char, "_")
                    ha_object_id = "s2m_" + device + "_{}".format("memory")
                    ha_name = title.title()
                    dtt = self.ha_discovery_template.format(ha_type, ha_object_id)
                    haconfig = ha_config(discovery_topic=dtt, name=ha_name, object_id=ha_object_id, state_topic=final_topic,
                                         device=device, icon=ha_icon, entity_type=ha_type, unit=ha_unit, 
                                         availability_topic=self.availability_topic, 
                                         payload_available="online",
                                         payload_not_available="offline")
                    self.myqtt.publish(haconfig[0], haconfig[1], retain=False)
            else:
                logging.warning("Not MacOS or PVE system")
        except Exception as e:
            logging.error(e, exc_info=True)
    
    def publish_argon(self):
        if self.config.ARGON:
            logging.debug("Getting fan speed")
            slug = "/fan_speed"
            final_topic = self.config.MQTT_BASE_TOPIC + slug
            ha_type = "sensor"
            ha_unit = "%"
            ha_icon = "mdi:fan"
            try:
                speed = get_argon_fan_speed()
                logging.info("Fan Speed: {}%".format(speed))
                self.myqtt.publish(final_topic, speed)
                if self.config.HA_DISCOVERY and not self.first_loop_done:
                    title = "Argon Fan Speed"
                    device = self.config.COMPUTER_NAME
                    for char in (" ", "-"):
                        device = device.replace(char, "_")
                    ha_object_id = "s2m_" + device + "_{}".format("fan_speed")
                    ha_name = "{}".format(title).title()
                    dtt = self.ha_discovery_template.format(ha_type, ha_object_id)
                    haconfig = ha_config(discovery_topic=dtt, name=ha_name, object_id=ha_object_id,
                                         state_topic=final_topic, device=device, icon=ha_icon,
                                         entity_type=ha_type, unit=ha_unit, 
                                         availability_topic=self.availability_topic, 
                                         payload_available="online",
                                         payload_not_available="offline")
                    self.myqtt.publish(haconfig[0], haconfig[1], retain=False)
            except Exception as e:
                logging.error(e, exc_info=True)
            logging.debug("Getting hdd temperatures")
            slug = "/disks/temperature"
            ha_type = "sensor"
            ha_class = "temperature"
            # ha_icon = "mdi:thermometer"
            ha_unit = "°C"
            try:
                temps = gethddtemp()
                for disk, temp in temps.items():
                    final_topic = self.config.MQTT_BASE_TOPIC + slug + "/" +disk
                    logging.info("{}: {}°C".format(disk, temp))
                    self.myqtt.publish(final_topic, temp)
                    if self.config.HA_DISCOVERY and not self.first_loop_done:
                        title = disk
                        for char in (" ", "-"):
                            disk = disk.lower().replace(char, "_")
                        device = self.config.COMPUTER_NAME
                        for char in (" ", "-"):
                            device = device.replace(char, "_")
                        ha_object_id = "s2m_"+device+"_{}_{}".format(disk, "temperature")
                        ha_name = "{} Temperature".format(title).title()
                        dtt = self.ha_discovery_template.format(ha_type, ha_object_id)
                        haconfig = ha_config(discovery_topic=dtt, name=ha_name, object_id=ha_object_id,
                                             state_topic=final_topic, device=device, entity_type=ha_type,
                                             unit=ha_unit, device_class=ha_class, 
                                             availability_topic=self.availability_topic, 
                                             payload_available="online",
                                             payload_not_available="offline")
                        self.myqtt.publish(haconfig[0], haconfig[1], retain=False)
            except Exception as e:
                logging.error(e, exc_info=True)

    def publish_lwt_binary_sensor(self):
        if self.config.HA_DISCOVERY:
            ha_type = "binary_sensor"
            ha_class = "connectivity"
            device = self.config.COMPUTER_NAME.replace(" ", "_").replace("-", "_")
            ha_object_id = f"s2m_{device}_lwt"
            ha_name = f"{self.config.COMPUTER_NAME} LWT"
            discovery_topic = self.ha_discovery_template.format(ha_type, ha_object_id)
            haconfig = ha_config(
                discovery_topic=discovery_topic,
                name=ha_name,
                object_id=ha_object_id,
                state_topic=self.lwt_topic,
                device=device,
                entity_type=ha_type,
                device_class=ha_class,
                payload_on="online",
                payload_off="offline"
            )
            self.myqtt.publish(haconfig[0], haconfig[1], retain=True)

    def publish_all(self):
        logging.debug("...publishing")
        self.myqtt.publish(self.lwt_topic, 'online')
        funcs = [self.publish_lwt_binary_sensor,
                 self.publish_mount_state,
                 self.publish_disk_space,
                 self.publish_cpu_temp,
                 self.publish_cpu_usage,
                 self.publish_ram,
                 self.publish_argon]
        for f in funcs:
            f()
        logging.info("Discovery complete!")
        self.first_loop_done = True


################################################################################################
################################       CALLBACKS      ##########################################
################################################################################################

    def process_user_callbacks(self, *args, **kwargs):
        logging.debug("Processing user callbacks...")
        if self.config.USER_CALLBACKS:
            import user_callbacks as uc
            ucb = self.config.CALLBACKS
            logging.debug(ucb)
            if not type(ucb) == dict:
                logging.warning("User callbacks aren't in a dictionary. They are a {}".format(type(ucb)))
                import ast
                ucb = ast.literal_eval(ucb)
            for k, v in ucb.items():
                    self.myqtt.topic_callbacks[k] = getattr(uc, v)
            logging.debug(self.myqtt.topic_callbacks)


    def s2m_set_publish_period(self, client, userdata, message):
        logging.debug("")
        # global PUBLISH_PERIOD
        try:
            new_publish_period = int(message.payload.decode("utf-8"))
            if new_publish_period != self.publish_period:
                self.publish_period = new_publish_period
                logging.info("Publish period has been set to {} seconds.".format(self.publish_period))
        except Exception as e:
            logging.error(e, exc_info=True)
            self.publish_period = self.config.PUBLISH_PERIOD

    def quit_s2m(self, client, userdata, message):
        logging.debug("")
        if message.payload.decode("utf-8") == "1":
            self.auto_reconnect =False
            logging.info("Quit called....")
            self.myqtt.publish(self.config.MQTT_BASE_TOPIC + "/callbacks/s2m_quit", "")
            self.myqtt.publish(self.lwt_topic, "offline", retain=True)
            client.loop_stop()
            client.disconnect()
    
    def cb_shutdown(self, client, userdata, message):
        mpl = message.payload.decode("utf-8")
        logging.debug(mpl)
        title = "[Shutdown]"
        if mpl == "1":
            logging.info("Attempting to poweroff...")
            self.myqtt.publish(self.config.MQTT_BASE_TOPIC + "/callbacks/shutdown", "")
            try:
                res = check_call(["shutdown", "-h", "now"])
            except Exception as e:
                logging.error(e, exc_info=True)
        else:
            logging.warning("{}: '{}': Not 1 recieved".format(title, mpl))
    
    def cb_reboot(self, client, userdata, message):
        mpl = message.payload.decode("utf-8")
        logging.debug(mpl)
        title = "[Reboot]"
        if mpl == "1":
            logging.info("Attempting to reboot...")
            self.myqtt.publish(self.config.MQTT_BASE_TOPIC + "/callbacks/reboot", "")
            try:
                res = check_call(["reboot", "now"])
            except Exception as e:
                logging.error(e, exc_info=True)
        else:
            logging.warning("{}: '{}': Not 1 recieved".format(title, mpl))




if __name__ == '__main__':
    try:
        config = sys.argv[1]
    except:
        config = os.path.join(os.path.dirname(os.path.abspath(__file__)), "s2m.conf")
    print("conf: ", config)
    s2m = System2Mqtt(config)
    time.sleep(1)
    s2m.run()
