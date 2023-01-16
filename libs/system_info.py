import psutil
import platform
import subprocess
import socket
import logging

# cpu_pct = psutil.cpu_percent(interval=0.1, percpu=False)
# load = psutil.getloadavg()
# mem = psutil.virtual_memory()
from libs.optizfs import OptiZFS

Platform = platform.system()

def set_proc(procpath):
    psutil.PROCFS_PATH = procpath

def get_hostname():
    return socket.gethostname()

def get_disks(procpath=None):
    if Platform == "Linux":
        set_proc(procpath)
    disks = psutil.disk_partitions(all=False)
    all_disks = []
    try:
        z = OptiZFS()
        pools = z.get_pools()
        for k, v in pools.items():
            all_disks.append(z.get_mountpoint(v))
    except Exception as e:
        logging.warning(e)
    if Platform == 'Darwin':
        excluded = ['/private/var/vm', "/Data"]
        for d in disks:
            if d in excluded:
                disks.remove(d)
        for d in disks:
            all_disks.append(d.mountpoint)
    else:
        for d in disks:
            all_disks.append(d.mountpoint)
    return all_disks

def get_disk_space(mount_path, return_type='percent', procpath=None):
    if Platform == "Linux":
        set_proc(procpath)
    space_dict = {}
    try:
        z = OptiZFS()
        pools = z.get_pools()
        for k, v in pools.items():
            if mount_path == z.get_mountpoint(v):
                storage = z.get_storage_percent(v)
                logging.debug("mp: {} - {}%".format(mount_path, storage))
                space_dict["percent"] = storage
                return space_dict.get(return_type)
    except Exception as e:
        logging.warning(e)
    space = psutil.disk_usage(mount_path)
    space_dict["total"] = space.total
    space_dict["used"] = space.used
    space_dict["free"] = space.free
    space_dict["percent"] = space.percent
    return space_dict.get(return_type)


def get_memory(return_type='percent', procpath=None):
    if Platform == "Linux":
        set_proc(procpath)
    mem_dict = {}
    mem = psutil.virtual_memory()
    try:
        mem_dict["total"] = mem.total
    except:
        mem_dict["total"] = ""
    try:
        mem_dict["used"] = mem.used
    except:
        mem_dict["used"] = ""
    try:
        mem_dict["free"] = mem.free
    except:
        mem_dict["free"] = ""
    try:
        mem_dict["percent"] = mem.percent
    except:
        mem_dict["percent"] = ""
    try:
        mem_dict["available"] = mem.available
    except:
        mem_dict["available"] = ""
    try:
        mem_dict["active"] = mem.active
    except:
        mem_dict["active"] = ""
    try:
        mem_dict["inactive"] = mem.inactive
    except:
        mem_dict["inactive"] = ""
    try:
        mem_dict["wired"] = mem.wired
    except:
        mem_dict["wired"] = ""
    return mem_dict.get(return_type)

def get_temps(procpath=None):
    if Platform == 'Darwin':
        try:
            task = subprocess.check_output(
                ["istats", "cpu", "temp", "--value-only"])
            temps = task.decode(encoding='UTF-8')
        except:
            logging.warning("Unable to get temperatures")
            temps = None
    else:
        try:
            if Platform == "Linux":
                set_proc(procpath)
            temps = psutil.sensors_temperatures()
        except:
            temps = None
    return temps

def get_cpu(procpath=None):
    if Platform == "Linux":
        set_proc(procpath)
    cpu = psutil.cpu_percent(interval=1)
    return cpu

def get_argon_fan_speed():
    with open("/tmp/fanspeed.txt") as e:
        speed = e.read()
    try:
        return int(float(speed))
    except FileNotFoundError:
        return None

###### MAC SPECIFIC #####

class MacSystemDetails():

    def __init__(self):

        if Platform != "Darwin":
            raise Exception("This is not a Mac.")

        self._overview = None
        self._error = None
        self._model_name = None
        self._model_id = None
        self._processor_name = None
        self._processor_speed = None
        self._processor_count = None
        self._core_count = None
        self._l2_cache = None
        self._l3_cache = None
        self._hyper_threading_tech = None
        self._memory = None
        self._boot_rom_version = None
        self._smc_version = None
        self._serial_number = None
        self._hardware_uuid = None

        task = subprocess.check_output(
            ['system_profiler', 'SPHardwareDataType'])

        output_string = task.decode(encoding='UTF-8')
        self._overview = output_string

        for line in self._overview.split("\n"):
            if ":" in line:
                splitline = line.split(":")
                splitline[1] = splitline[1].strip()
                if "Model Name" in splitline[0]:
                    self._model_name = splitline[1]
                elif "Model Identifier" in splitline[0]:
                    self._model_id = splitline[1]
                elif "Processor Name" in splitline[0]:
                    self._processor_name = splitline[1]
                elif "Processor Speed" in splitline[0]:
                    self._processor_speed = splitline[1]
                elif "Number of Processors" in splitline[0]:
                    self._processor_count = splitline[1]
                elif "Total Number of Cores" in splitline[0]:
                    self._core_count= splitline[1]
                elif "L2 Cache (per Core)" in splitline[0]:
                    self._l2_cache = splitline[1]
                elif "L3 Cache" in splitline[0]:
                    self._l3_cache = splitline[1]
                elif "Hyper-Threading Technology" in splitline[0]:
                    self._hyper_threading_tech = splitline[1]
                elif "Memory" in splitline[0]:
                    self._memory = splitline[1]
                elif "Boot ROM Version" in splitline[0]:
                    self._boot_rom_version = splitline[1]
                elif "SMC Version (system)" in splitline[0]:
                    self._smc_version = splitline[1]
                elif "Serial Number (system)" in splitline[0]:
                    self._serial_number = splitline[1]
                elif "Hardware UUID" in splitline[0]:
                    self._hardware_uuid = splitline[1]
                else:
                    pass

    def modelName(self):
        return self._model_name

    def modelID(self):
        return self._model_id

    def processorName(self):
        return self._processor_name

    def processorSpeed(self):
        return self._processor_speed

    def processorCount(self):
        return self._processor_count

    def coreCount(self):
        return self._core_count

    def l2Cache(self):
        return self._l2_cache

    def l3Cache(self):
        return self._l3_cache

    def hyperThreading(self):
        return self._hyper_threading_tech

    def memory(self):
        return self._memory

    def bootRom(self):
        return self._boot_rom_version

    def smc(self):
        return self._smc_version

    def serial(self):
        return self._serial_number

    def uuid(self):
        return self._hardware_uuid

    def overview(self):
        return self._overview