# MQTT Topics Reference

This page documents all MQTT topics that system2mqtt publishes to and subscribes to.

---

## Topic Structure

All topics are prefixed by the base topic. Unless overridden with `MQTT_BASE_TOPIC`, the base topic is:

```
system2mqtt/<COMPUTER_NAME>
```

For example, for `COMPUTER_NAME=MyServer`:

```
system2mqtt/MyServer/cpu/usage
system2mqtt/MyServer/memory
...
```

---

## Published Topics

### Availability

| Topic | Values | Description |
|-------|--------|-------------|
| `<base>/LWT` | `online` / `offline` | Last Will & Testament. Published as `online` on connect; the broker publishes `offline` automatically if the connection is lost. This topic is **retained**. |

### CPU

| Topic | Values | Description |
|-------|--------|-------------|
| `<base>/cpu/usage` | Integer `0`–`100` | CPU usage as a percentage. |
| `<base>/cpu/temperature` | Float (°C) | Highest CPU core temperature in degrees Celsius. Only available on Linux (via `/sys/class/thermal`) and macOS (via `istats`). |

### Memory

| Topic | Values | Description |
|-------|--------|-------------|
| `<base>/memory` | Float `0.0`–`100.0` | RAM usage as a percentage. |

### Disk Storage

For each disk detected (subject to `STORAGE_INCLUDE` / `STORAGE_EXCLUDE` filters):

| Topic | Values | Description |
|-------|--------|-------------|
| `<base>/disks/storage/<label>` | Float `0.0`–`100.0` | Disk space used as a percentage. `<label>` is the disk/partition label or mount-point name. |
| `<base>/disks/mount/<label>` | `mounted` / `unmounted` | Whether the disk is currently mounted. |

### Argon ONE Case (when `ARGON=True`)

| Topic | Values | Description |
|-------|--------|-------------|
| `<base>/fan_speed` | Integer `0`–`100` | Argon ONE case fan speed as a percentage. |
| `<base>/disks/temperature/<disk>` | Float (°C) | HDD temperature reported by `smartctl`. `<disk>` is the device name (e.g. `sda`). |

---

## Subscribed Topics (Built-in Commands)

system2mqtt subscribes to these topics automatically. Send a message to one of them to trigger the corresponding action.

| Topic | Payload | Effect |
|-------|---------|--------|
| `<base>/tele/PUBLISH_PERIOD` | Integer (seconds) | Change the publish interval at runtime without restarting. Example: send `30` to publish every 30 seconds. |
| `<base>/callbacks/s2m_quit` | _(any)_ | Gracefully stop the system2mqtt application. |
| `<base>/callbacks/shutdown` | `1` | Shut down the host system (`shutdown` command). **Use with caution.** Requires appropriate OS privileges. |
| `<base>/callbacks/reboot` | `1` | Reboot the host system (`reboot` command). **Use with caution.** Requires appropriate OS privileges. |

---

## User-Defined Callback Topics

When `USER_CALLBACKS=True`, additional topics are subscribed based on the `CALLBACKS` configuration. You define both the topic and the Python function to invoke. See [Advanced Usage](advanced-usage.md) for details.

---

## Example: Subscribing with mosquitto_sub

Subscribe to all topics for a given computer:

```sh
mosquitto_sub -h 192.168.1.100 -t "system2mqtt/MyServer/#" -v
```

Subscribe to a single topic:

```sh
mosquitto_sub -h 192.168.1.100 -t "system2mqtt/MyServer/cpu/usage" -v
```

---

## Example: Sending Commands with mosquitto_pub

Change the publish interval to 30 seconds:

```sh
mosquitto_pub -h 192.168.1.100 -t "system2mqtt/MyServer/tele/PUBLISH_PERIOD" -m "30"
```

Gracefully stop system2mqtt:

```sh
mosquitto_pub -h 192.168.1.100 -t "system2mqtt/MyServer/callbacks/s2m_quit" -m "1"
```

Reboot the machine:

```sh
mosquitto_pub -h 192.168.1.100 -t "system2mqtt/MyServer/callbacks/reboot" -m "1"
```
