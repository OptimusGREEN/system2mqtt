# system2mqtt

**system2mqtt** is a lightweight Python utility that periodically collects system information (CPU, memory, and disk usage) and publishes it to an MQTT broker. It's designed to help you monitor your systems and integrate their status into MQTT-based home automation, dashboards, or monitoring tools.

## Features

- Collects CPU, memory, and disk usage statistics from your system.
- Publishes metrics to your configured MQTT broker at regular intervals.
- Configurable via a simple configuration file.
- Supports running directly on bare metal (Linux/macOS) or inside a Docker container.
- Docker image available for Proxmox API access.
- Tested on Linux and macOS.

## Getting Started

### Prerequisites

- Python 3.x
- An MQTT broker (local or remote)

### Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/OptimusGREEN/system2mqtt.git
    cd system2mqtt
    ```

2. **Configure:**
    - Copy or edit the provided example configuration file.
    - At minimum, set your computer name.
    - Example configuration options:
      ```
      COMPUTER_NAME=MyTestComputer1                   # Required: 

      ##### UNCOMMENT ANY BELOW OPTIONS AS REQUIRED

      #LOG_DIR=path/to/my/logs                         ### Optional: default: ./logs
      #LOG_FILENAME=system2mqtt.log                    ### Optional: default: system2mqtt.log 
      #OLD_LOG_FILENAME=old_system2mqtt.log            ### Optional: default: old_system2mqtt.log 
      #DEBUG_LOG=True                                  ### Optional: default: False

      #PUBLISH_PERIOD=30                               ### Optional: default: 30 (seconds)
      #MQTT_BASE_TOPIC=system2mqtt/MyTestComputer1     ### Optional: default: system2mqtt/<COMPUTER_NAME>
      #MQTT_HOST=192.168.0.14                          ### Optional: default: localhost
      #MQTT_USER=myusername                            ### Optional: default: None
      #MQTT_PASSWORD=mypassword                        ### Optional: default: None
      ```

3. **Run:**
    ```sh
    python3 run.py
    ```

### Docker

A Docker image is available for Proxmox API access:

- [Docker Hub: optimusgreen/system2mqtt](https://hub.docker.com/repository/docker/optimusgreen/system2mqtt)
- Note: Docker image is currently only available for Proxmox API usage, not for bare metal monitoring.

## Usage

- The script will publish your system's metrics to the MQTT topic you configure.
- Use your MQTT broker and dashboard/automation tool of choice to subscribe and visualize or act on these metrics.

## Configuration Options

- `COMPUTER_NAME`: Unique name for your system (required).
- `LOG_DIR`: Directory for log files (optional).
- `LOG_FILENAME`: Name of the log file (optional).
- `OLD_LOG_FILENAME`: Name of the old log file (optional).
- `DEBUG_LOG`: Enable debug logging (optional).
- `PUBLISH_PERIOD`: How often to publish (in seconds, default: 30).
- `MQTT_BASE_TOPIC`: Base MQTT topic to publish to.
- `MQTT_HOST`: MQTT broker address (default: localhost).
- `MQTT_USER` / `MQTT_PASSWORD`: MQTT authentication (optional).

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE).

## Notes

- Only tested on Linux and macOS.
- Contributions and issues are welcome!
