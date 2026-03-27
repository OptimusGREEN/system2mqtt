# Getting Started

This guide walks you through installing and running system2mqtt for the first time.

---

## Prerequisites

- **Python 3.6+** installed on your system
- A running **MQTT broker** (e.g. [Mosquitto](https://mosquitto.org/), [EMQX](https://www.emqx.io/), or the broker built into Home Assistant)
- Internet access to install Python dependencies (first run only)

### Optional prerequisites

| Feature | Requirement |
|---------|-------------|
| Proxmox monitoring | A Proxmox VE node reachable on your network |
| Disk temperature (Argon ONE) | `smartmontools` package installed (`apt install smartmontools`) |
| macOS CPU temperature | `istats` gem (`gem install iStats`) |

---

## Installation

### 1. Clone the repository

```sh
git clone https://github.com/OptimusGREEN/system2mqtt.git
cd system2mqtt
```

### 2. Create your configuration file

Copy the example configuration file and edit it:

```sh
cp s2m.conf.example s2m.conf
```

At minimum, set `COMPUTER_NAME` to a unique name for this machine. All other settings have sensible defaults.

```ini
COMPUTER_NAME=MyComputer
```

To connect to an MQTT broker that is not running locally, also set `MQTT_HOST`:

```ini
COMPUTER_NAME=MyComputer
MQTT_HOST=192.168.1.100
```

> See the full [Configuration Reference](configuration.md) for all available options.

### 3. Run

Use the `run.py` watchdog script. It will:

- Automatically create a Python virtual environment in `./venv`
- Install all required dependencies from `deps.txt`
- Start `s2m.py` and restart it if it crashes

```sh
python3 run.py
```

To pass a custom config file path:

```sh
python3 run.py /path/to/my/s2m.conf
```

To force-reinstall Python dependencies (e.g. after an update):

```sh
python3 run.py --force-reinstall
```

---

## Verifying It Works

Once running, you should see log output similar to:

```
[MyComputer]: [INFO] s2m:42 - 2024-01-01 12:00:00 - Starting System2Mqtt
[MyComputer]: [INFO] s2m:55 - 2024-01-01 12:00:00 - Connecting to MQTT broker at localhost:1883
[MyComputer]: [INFO] s2m:60 - 2024-01-01 12:00:01 - MQTT connected
[MyComputer]: [INFO] s2m:80 - 2024-01-01 12:00:01 - Publishing metrics...
```

You can verify MQTT messages are arriving using any MQTT client. For example, with `mosquitto_sub`:

```sh
# Subscribe to all system2mqtt topics for your computer
mosquitto_sub -h localhost -t "system2mqtt/MyComputer/#" -v
```

Expected output:

```
system2mqtt/MyComputer/LWT online
system2mqtt/MyComputer/cpu/usage 12
system2mqtt/MyComputer/memory 45.3
system2mqtt/MyComputer/disks/storage/sda1 67.2
...
```

---

## Running Directly (without the watchdog)

You can also run the main script directly, bypassing the watchdog. You must first install dependencies manually:

```sh
python3 -m venv venv
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate         # Windows
pip install -r deps.txt

python3 s2m.py                  # uses s2m.conf in current directory
python3 s2m.py /path/to/s2m.conf
```

---

## Next Steps

- **[Configuration Reference](configuration.md)** — explore all available options
- **[MQTT Topics](mqtt-topics.md)** — understand what gets published and where
- **[Home Assistant Integration](home-assistant.md)** — auto-discover entities in Home Assistant
- **[Running as a Service](running-as-a-service.md)** — run system2mqtt automatically on boot
- **[Docker Deployment](docker.md)** — run in a container (especially useful for Proxmox)
