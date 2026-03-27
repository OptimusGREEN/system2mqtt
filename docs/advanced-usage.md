# Advanced Usage

This page covers advanced features of system2mqtt including user-defined callbacks, built-in remote commands, Argon ONE Raspberry Pi case support, and storage filtering.

---

## User-Defined MQTT Callbacks

You can define custom Python functions that are triggered when a specific MQTT message is received.

### Setup

**Step 1:** Create `user_callbacks.py` in the root of the repository by copying the example:

```sh
cp user_callbacks.py.example user_callbacks.py
```

**Step 2:** Define your functions in `user_callbacks.py`. Each function must accept the following signature:

```python
def my_function(client, userdata, message, *args, **kwargs):
    payload = message.payload.decode("utf-8")
    # do something...
```

| Parameter | Description |
|-----------|-------------|
| `client` | The Paho MQTT client instance. Use `client.publish(topic, payload)` to publish back. |
| `userdata` | Arbitrary user data (usually not needed). |
| `message` | The MQTT message object. Access payload via `message.payload.decode("utf-8")`. |

**Step 3:** Map MQTT topics to your functions in `s2m.conf`:

```ini
USER_CALLBACKS=True
CALLBACKS={'system2mqtt/MyComputer/callbacks/lights': 'toggleLights', 'system2mqtt/MyComputer/callbacks/alarm': 'triggerAlarm'}
```

The key is the **full MQTT topic** to subscribe to. The value is the **function name** from `user_callbacks.py`.

### Example

```python
# user_callbacks.py

def toggleLights(client, userdata, message, *args, **kwargs):
    payload = message.payload.decode("utf-8")
    if payload == "on":
        print("Turning lights ON")
        # add your light control logic here
    elif payload == "off":
        print("Turning lights OFF")

def triggerAlarm(client, userdata, message, *args, **kwargs):
    payload = message.payload.decode("utf-8")
    if payload == "1":
        print("Alarm triggered!")
        # publish a confirmation
        client.publish("system2mqtt/MyComputer/alarm/status", "triggered")
```

Trigger from the command line:

```sh
mosquitto_pub -h localhost -t "system2mqtt/MyComputer/callbacks/lights" -m "on"
```

---

## Built-in Remote Commands

system2mqtt subscribes to several command topics automatically. No extra configuration is needed.

| Topic | Payload | Effect |
|-------|---------|--------|
| `<base>/tele/PUBLISH_PERIOD` | Integer (seconds) | Change the publish interval at runtime. |
| `<base>/callbacks/s2m_quit` | _(any)_ | Gracefully stop the application. |
| `<base>/callbacks/shutdown` | `1` | Shut down the host system. |
| `<base>/callbacks/reboot` | `1` | Reboot the host system. |

> **Warning:** The `shutdown` and `reboot` commands execute operating system commands. Ensure your MQTT broker is secured appropriately to prevent unauthorized access.

**Example — change publish interval to every 10 seconds:**

```sh
mosquitto_pub -h localhost -t "system2mqtt/MyServer/tele/PUBLISH_PERIOD" -m "10"
```

---

## Argon ONE Raspberry Pi Case

The [Argon ONE](https://www.argon40.com/products/argon-one-m-2-case-for-raspberry-pi-4) and [Argon EON](https://www.argon40.com/products/argon-eon-pi-nas) cases for Raspberry Pi include a programmable fan and (in the EON) support for attached storage. system2mqtt can monitor both.

### Enable Argon ONE support

```ini
ARGON=True
```

### What gets monitored

| Metric | Source |
|--------|--------|
| Fan speed (`fan_speed`) | Read from `/tmp/fanspeed.txt` (set by the Argon daemon), or calculated from CPU temperature thresholds in `/etc/argoneon.conf` or `/etc/argononed.conf`. |
| HDD temperatures (`disks/temperature/<disk>`) | Read via `smartctl` from attached drives. |

### Requirements

- The Argon ONE / EON daemon must be installed for fan speed to be read from `/tmp/fanspeed.txt`. Without it, system2mqtt calculates fan speed from CPU temperature thresholds.
- `smartmontools` must be installed: `sudo apt install smartmontools`
- Reading disk temperatures typically requires elevated privileges. Run with `sudo` or grant permissions via `sudoers`.

---

## Storage Filtering

By default, system2mqtt reports all mounted disks. You can filter which disks are included.

### Include specific disks

```ini
STORAGE_INCLUDE=["sysroot", "mynas"]
```

When `STORAGE_INCLUDE` is set, **only** the listed disk labels are reported. All others are ignored.

### Exclude specific disks

```ini
STORAGE_EXCLUDE=["tmpfs", "devtmpfs", "udev"]
```

When `STORAGE_EXCLUDE` is set, the listed disk labels are **skipped**. All others are reported.

> `STORAGE_INCLUDE` takes precedence over `STORAGE_EXCLUDE`. If both are set, only `STORAGE_INCLUDE` is used.

### Finding disk labels

Disk labels correspond to the partition or device name reported by `psutil`. To see what labels your system uses, enable debug logging temporarily:

```ini
DEBUG_LOG=True
```

Then look for log entries listing disk partitions on startup.

---

## ZFS Support

system2mqtt includes support for ZFS pools via the `zfslib` library. ZFS pools are detected automatically alongside standard partitions and included in disk storage reporting.

No extra configuration is required. ZFS pools appear in storage topics using their pool name as the label:

```
system2mqtt/MyServer/disks/storage/rpool
system2mqtt/MyServer/disks/mount/rpool
```
