# system2mqtt

**system2mqtt** is a lightweight Python utility that periodically collects system information (CPU, memory, and disk usage) and publishes it to an MQTT broker. It is designed to help you monitor your systems and integrate their status into MQTT-based home automation platforms, dashboards, or monitoring tools.

## Features

- Collects CPU usage, CPU temperature, memory usage, and disk usage/mount status.
- Publishes metrics to your MQTT broker at a configurable interval.
- **Home Assistant MQTT Discovery** — entities auto-appear in Home Assistant.
- **Proxmox VE support** — monitor a Proxmox node via its API (ideal for Docker deployment).
- **Argon ONE Raspberry Pi case** — fan speed and HDD temperature monitoring.
- **User-defined MQTT callbacks** — trigger custom Python functions via MQTT messages.
- **Built-in remote commands** — reboot, shutdown, or adjust publish rate over MQTT.
- Automatic watchdog via `run.py` — restarts on crash, manages its own virtual environment.
- Configurable via a simple `.env`-style configuration file.
- Supports Linux and macOS (bare metal or Docker).

## Quick Start

```sh
# 1. Clone the repository
git clone https://github.com/OptimusGREEN/system2mqtt.git
cd system2mqtt

# 2. Create your configuration file
cp s2m.conf.example s2m.conf
# Edit s2m.conf — at minimum set COMPUTER_NAME and MQTT_HOST

# 3. Run (auto-creates venv and installs dependencies)
python3 run.py
```

> See **[Getting Started](docs/getting-started.md)** for full installation instructions.

## Documentation

| Page | Description |
|------|-------------|
| [Getting Started](docs/getting-started.md) | Prerequisites, installation, and first run |
| [Configuration Reference](docs/configuration.md) | All configuration options explained |
| [MQTT Topics](docs/mqtt-topics.md) | Published topics, payloads, and built-in commands |
| [Home Assistant Integration](docs/home-assistant.md) | Auto-discovery setup and entity reference |
| [Proxmox Monitoring](docs/proxmox.md) | Monitoring a Proxmox VE node via API |
| [Docker Deployment](docs/docker.md) | Running system2mqtt in a Docker container |
| [Advanced Usage](docs/advanced-usage.md) | Callbacks, Argon ONE, storage filtering |
| [Running as a Service](docs/running-as-a-service.md) | Systemd (Linux) and LaunchAgent (macOS) |
| [Troubleshooting](docs/troubleshooting.md) | Common issues and debugging tips |

## Minimal Configuration

```ini
# s2m.conf
COMPUTER_NAME=MyComputer    # Required — unique name for this system
MQTT_HOST=192.168.1.100     # Optional — defaults to localhost
```

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE).

## Notes

- Tested on Linux and macOS.
- Some metrics (e.g. disk temperatures via `smartctl`) may require elevated privileges.
- Contributions and issues are welcome!
