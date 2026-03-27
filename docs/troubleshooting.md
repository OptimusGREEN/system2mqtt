# Troubleshooting

This page covers common issues and how to resolve them.

---

## Enable Debug Logging

The first step for any problem is to enable debug logging. Add this to your `s2m.conf` and restart:

```ini
DEBUG_LOG=True
```

Debug output is written to both the log file and the console. This makes it much easier to see what system2mqtt is doing at each step.

---

## Common Issues

### system2mqtt won't connect to the MQTT broker

**Symptoms:** Log shows "Connection refused" or the application retries indefinitely.

**Causes and fixes:**

1. **Wrong broker address** — verify `MQTT_HOST` and `MQTT_PORT` in `s2m.conf`.
2. **Broker not running** — confirm your MQTT broker is running:
   ```sh
   # For Mosquitto:
   sudo systemctl status mosquitto
   ```
3. **Firewall blocking port 1883** — check that port 1883 is open on the broker host.
4. **Authentication failure** — if your broker requires credentials, set `MQTT_USER` and `MQTT_PASSWORD`. If it does not require credentials, remove those lines.
5. **Broker only listens on localhost** — if your broker is on the same machine but only bound to `127.0.0.1`, either use `MQTT_HOST=localhost` or configure the broker to listen on `0.0.0.0`.

---

### No entities appear in Home Assistant

**Symptoms:** `HA_DISCOVERY=True` is set but nothing shows up in Home Assistant.

**Causes and fixes:**

1. **MQTT integration not configured** — go to **Settings → Devices & Services → Add Integration** and add the MQTT integration pointing to your broker.
2. **Discovery prefix mismatch** — the default prefix is `homeassistant`. If your Home Assistant uses a different prefix, update `HA_DISCOVERY_BASE` to match.
3. **Broker mismatch** — system2mqtt and Home Assistant must be connected to the **same** MQTT broker.
4. **Discovery messages not published yet** — discovery messages are only published on the first publish cycle. Wait for the first `PUBLISH_PERIOD` interval, or restart system2mqtt.
5. **Check with MQTT Explorer** — subscribe to `homeassistant/#` on your broker to verify discovery messages are being published.

---

### CPU temperature is not available

**Symptoms:** `cpu/temperature` topic is never published, or shows `0`.

**Causes and fixes:**

- **Linux:** Requires temperature sensors exposed via `/sys/class/thermal`. This is common on most Linux systems. If missing, your hardware or kernel drivers may not support it.
- **macOS:** Requires `istats` to be installed:
  ```sh
  sudo gem install iStats
  ```
- **Docker:** Temperature sensors are not accessible from inside a container.
- **Proxmox mode:** CPU temperature is not available via the Proxmox API.

---

### Disk temperature is not available (Argon ONE)

**Symptoms:** `ARGON=True` is set but `disks/temperature/<disk>` topics are not published.

**Causes and fixes:**

1. **`smartmontools` not installed:**
   ```sh
   sudo apt install smartmontools
   ```
2. **Insufficient permissions** — `smartctl` requires root or `sudo` access. Run system2mqtt with elevated privileges, or configure `sudoers` to allow the user to run `smartctl` without a password:
   ```
   youruser ALL=(ALL) NOPASSWD: /usr/sbin/smartctl
   ```

---

### No disk storage metrics published

**Symptoms:** `disks/storage/<label>` topics are missing for some or all disks.

**Causes and fixes:**

1. **Disk is excluded** — check `STORAGE_EXCLUDE` in your config. The disk label may match an excluded entry.
2. **`STORAGE_INCLUDE` is set** — if `STORAGE_INCLUDE` is configured, only explicitly listed disks are reported. Add the missing disk to the list.
3. **Label mismatch** — enable `DEBUG_LOG=True` to see the exact disk labels that are detected at startup.

---

### Proxmox connection fails

**Symptoms:** Log shows API errors or authentication failures when `PVE_SYSTEM=True`.

**Causes and fixes:**

1. **Wrong credentials** — verify `PVE_USER` and `PVE_PASSWORD`.
2. **Wrong host** — verify `PVE_HOST` is reachable from the machine running system2mqtt (`ping <PVE_HOST>`).
3. **Wrong node name** — verify `PVE_NODE_NAME` matches the node name shown in the Proxmox UI.
4. **Proxmox API port blocked** — the Proxmox API uses port `8006`. Ensure it is accessible.
5. **User lacks permissions** — ensure the Proxmox user has at least `Sys.Audit` and `Datastore.Audit` privileges on the `/` path.

---

### `run.py` fails to create the virtual environment

**Symptoms:** Error during startup like `venv creation failed` or `pip install failed`.

**Causes and fixes:**

1. **Python 3 not found** — ensure `python3` is in your `PATH`.
2. **`venv` module not available** — install it:
   ```sh
   # Debian/Ubuntu:
   sudo apt install python3-venv
   ```
3. **Disk full** — check available disk space with `df -h`.
4. **Permission error** — ensure you have write access to the system2mqtt directory.
5. **Force reinstall** — if the virtual environment is corrupted, force a rebuild:
   ```sh
   python3 run.py --force-reinstall
   ```

---

### Log file is not being created

**Symptoms:** No log file appears in `./logs/`.

**Causes and fixes:**

1. The log directory is created automatically. If there is a permission issue, set `LOG_DIR` to a path where you have write access:
   ```ini
   LOG_DIR=/tmp/s2m-logs
   ```
2. When running in debug mode, log output is also printed to the console, so you can see messages even without a log file.

---

## Getting More Help

- Check the [GitHub Issues](https://github.com/OptimusGREEN/system2mqtt/issues) page for known issues and solutions.
- Enable `DEBUG_LOG=True` and include the log output when reporting a bug.
- Provide your `s2m.conf` (with passwords removed) when asking for help.
