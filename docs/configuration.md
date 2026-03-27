# Configuration Reference

system2mqtt is configured through a `.env`-style file (default: `s2m.conf` in the working directory). All keys are uppercase. Lines beginning with `#` are comments.

---

## Loading Order

1. `s2m.conf` in the current working directory (default)
2. A path passed as a command-line argument: `python3 run.py /path/to/my.conf`

---

## Required Options

| Key | Description |
|-----|-------------|
| `COMPUTER_NAME` | A unique identifier for this system. Used in MQTT topics and log output. **Required.** |

---

## Logging

| Key | Default | Description |
|-----|---------|-------------|
| `LOG_DIR` | `./logs` | Directory where log files are written. Created automatically if it does not exist. |
| `LOG_FILENAME` | `system2mqtt.log` | Name of the active log file. |
| `OLD_LOG_FILENAME` | `old_system2mqtt.log` | Name of the previous log file (rotated on startup). |
| `DEBUG_LOG` | `False` | Set to `True` to enable verbose debug logging. Debug output is also printed to the console. |

---

## MQTT

| Key | Default | Description |
|-----|---------|-------------|
| `MQTT_HOST` | `localhost` | Hostname or IP address of the MQTT broker. |
| `MQTT_PORT` | `1883` | TCP port of the MQTT broker. |
| `MQTT_USER` | _(none)_ | Username for MQTT broker authentication. |
| `MQTT_PASSWORD` | _(none)_ | Password for MQTT broker authentication. |
| `MQTT_BASE_TOPIC` | `system2mqtt/<COMPUTER_NAME>` | Base MQTT topic. All metrics are published under this prefix. |

---

## Publishing

| Key | Default | Description |
|-----|---------|-------------|
| `PUBLISH_PERIOD` | `60` | How often (in seconds) to collect and publish metrics. Can also be changed at runtime via MQTT — see [MQTT Topics](mqtt-topics.md). |

---

## System / Platform

| Key | Default | Description |
|-----|---------|-------------|
| `PROCPATH` | `/proc` | Path to the Linux `proc` filesystem. Change this if running in a container where `/proc` is mounted at a different path. |
| `MACOS` | _(auto-detected)_ | Set to `True` to force macOS mode. Usually auto-detected. |

---

## Storage Filtering

By default, all mounted disks are included. Use these options to filter which disks are reported.

| Key | Default | Description |
|-----|---------|-------------|
| `STORAGE_INCLUDE` | _(none)_ | JSON list of disk labels to **include**. When set, only listed disks are reported. Takes precedence over `STORAGE_EXCLUDE`. Example: `["sysroot", "data"]` |
| `STORAGE_EXCLUDE` | _(none)_ | JSON list of disk labels to **exclude**. Ignored when `STORAGE_INCLUDE` is set. Example: `["tmpfs", "udev"]` |

**Example:**

```ini
# Only report these two disks
STORAGE_INCLUDE=["sysroot", "myexternaldrive"]

# OR: report everything except these
STORAGE_EXCLUDE=["idontwantthisdriveincluded"]
```

---

## Argon ONE Raspberry Pi Case

| Key | Default | Description |
|-----|---------|-------------|
| `ARGON` | `False` | Set to `True` to enable Argon ONE case fan and HDD temperature monitoring. |

When enabled, system2mqtt will:

- Read fan speed from `/tmp/fanspeed.txt` (set by the Argon ONE daemon), or calculate it from CPU temperature using thresholds in `/etc/argoneon.conf` or `/etc/argononed.conf`.
- Read HDD temperatures using `smartctl` (requires `smartmontools` to be installed, and typically elevated privileges).

> **Note:** Reading disk temperatures via `smartctl` may require running with `sudo` or granting the user appropriate permissions.

---

## Proxmox VE

| Key | Default | Description |
|-----|---------|-------------|
| `PVE_SYSTEM` | `False` | Set to `True` to monitor a Proxmox VE node via its API instead of the local system. |
| `PVE_HOST` | `localhost` | Hostname or IP address of the Proxmox VE server. |
| `PVE_NODE_NAME` | `pve` | The Proxmox node name as it appears in the Proxmox UI. |
| `PVE_USER` | `root@pam` | Proxmox user account (e.g. `root@pam` or `monitor@pve`). |
| `PVE_PASSWORD` | _(none)_ | Password for the Proxmox user. Required when `PVE_SYSTEM=True`. |

> See the [Proxmox Monitoring](proxmox.md) page for a full setup guide.

---

## User Callbacks

| Key | Default | Description |
|-----|---------|-------------|
| `USER_CALLBACKS` | `False` | Set to `True` to enable user-defined MQTT-triggered callback functions. |
| `CALLBACKS` | _(none)_ | A dictionary (as a string) mapping MQTT topics to function names defined in `user_callbacks.py`. |

**Format:**

```ini
USER_CALLBACKS=True
CALLBACKS={'system2mqtt/MyComputer/callbacks/myfunc': 'myFunctionName'}
```

> See the [Advanced Usage](advanced-usage.md) page for a full callbacks guide.

---

## Home Assistant Discovery

| Key | Default | Description |
|-----|---------|-------------|
| `HA_DISCOVERY` | `False` | Set to `True` to publish Home Assistant MQTT discovery messages. Entities will automatically appear in Home Assistant. |
| `HA_DISCOVERY_BASE` | `homeassistant` | The discovery prefix used in discovery topics. Must match the MQTT discovery prefix configured in Home Assistant (default: `homeassistant`). |

> See the [Home Assistant Integration](home-assistant.md) page for details.

---

## Full Example Configuration

```ini
# s2m.conf — system2mqtt configuration

# ── Required ──────────────────────────────────────────────────────────────────
COMPUTER_NAME=MyServer

# ── Logging ───────────────────────────────────────────────────────────────────
#LOG_DIR=./logs
#LOG_FILENAME=system2mqtt.log
#OLD_LOG_FILENAME=old_system2mqtt.log
#DEBUG_LOG=False

# ── MQTT ──────────────────────────────────────────────────────────────────────
#MQTT_HOST=localhost
#MQTT_PORT=1883
#MQTT_USER=myusername
#MQTT_PASSWORD=mypassword
#MQTT_BASE_TOPIC=system2mqtt/MyServer

# ── Publishing ────────────────────────────────────────────────────────────────
#PUBLISH_PERIOD=60

# ── Storage Filtering ─────────────────────────────────────────────────────────
#STORAGE_INCLUDE=["sysroot", "data"]
#STORAGE_EXCLUDE=["tmpfs"]

# ── Argon ONE Case (Raspberry Pi) ─────────────────────────────────────────────
#ARGON=False

# ── Proxmox VE ────────────────────────────────────────────────────────────────
#PVE_SYSTEM=False
#PVE_HOST=192.168.1.50
#PVE_NODE_NAME=pve
#PVE_USER=root@pam
#PVE_PASSWORD=mysecretpassword

# ── User Callbacks ────────────────────────────────────────────────────────────
#USER_CALLBACKS=False
#CALLBACKS={'system2mqtt/MyServer/callbacks/testcb1': 'cb1'}

# ── Home Assistant Discovery ──────────────────────────────────────────────────
#HA_DISCOVERY=False
#HA_DISCOVERY_BASE=homeassistant
```
