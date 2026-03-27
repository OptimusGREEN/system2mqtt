# Home Assistant Integration

system2mqtt supports [MQTT Discovery](https://www.home-assistant.io/integrations/mqtt/#mqtt-discovery), which allows entities to appear automatically in Home Assistant without any manual configuration.

---

## Prerequisites

1. The [MQTT Integration](https://www.home-assistant.io/integrations/mqtt/) must be configured in Home Assistant and connected to the same broker that system2mqtt publishes to.
2. MQTT Discovery must be enabled in the MQTT integration (it is on by default).

---

## Enabling Discovery

Add the following to your `s2m.conf`:

```ini
HA_DISCOVERY=True
```

Optionally, if you have changed the MQTT discovery prefix in Home Assistant from the default:

```ini
HA_DISCOVERY_BASE=homeassistant   # default — match your HA setting
```

After restarting system2mqtt, entities will appear in Home Assistant under **Settings → Devices & Services → MQTT**.

---

## Discovered Entities

For each system being monitored, system2mqtt creates a **device** in Home Assistant and registers the following entities:

| Entity | Type | Unit | Device Class | Icon |
|--------|------|------|--------------|------|
| `<Name> CPU Usage` | Sensor | `%` | `power_factor` | `mdi:cpu-64-bit` |
| `<Name> CPU Temperature` | Sensor | `°C` | `temperature` | `mdi:thermometer` |
| `<Name> Memory Usage` | Sensor | `%` | `power_factor` | `mdi:memory` |
| `<Name> <Disk> Storage` | Sensor | `%` | `power_factor` | `mdi:harddisk` |
| `<Name> <Disk> Mount` | Binary Sensor | — | `connectivity` | `mdi:harddisk` |
| `<Name> Fan Speed` | Sensor | `%` | — | `mdi:fan` | *(Argon ONE only)* |
| `<Name> <Disk> Temperature` | Sensor | `°C` | `temperature` | `mdi:thermometer` | *(Argon ONE only)* |

### Device information

Each monitored system appears as a single device in Home Assistant:

- **Name:** `S2M <ComputerName>` (e.g. `S2M Myserver`)
- **Manufacturer:** `TeamGREEN Tech`
- **Model:** `System2Mqtt`
- **Identifiers:** `<computer_name>` (lowercase)

---

## Discovery Topic Format

Discovery messages are published to:

```
<HA_DISCOVERY_BASE>/<component>/<object_id>/config
```

For example:

```
homeassistant/sensor/s2m_myserver_cpu/config
homeassistant/sensor/s2m_myserver_memory/config
homeassistant/binary_sensor/s2m_myserver_disk_sda1/config
```

---

## Availability Tracking

All entities use the LWT topic for availability tracking. When the system2mqtt process stops or loses connection, all entities will show as **unavailable** in Home Assistant.

- **Available payload:** `online`
- **Unavailable payload:** `offline`
- **LWT topic:** `<MQTT_BASE_TOPIC>/LWT`

---

## Example Discovery Payload

The following is an example discovery payload for a CPU usage sensor:

```json
{
  "name": "MyServer CPU Usage",
  "unique_id": "s2m_myserver_cpu",
  "object_id": "s2m_myserver_cpu",
  "state_topic": "system2mqtt/MyServer/cpu/usage",
  "device": {
    "identifiers": ["myserver"],
    "name": "S2M Myserver",
    "manufacturer": "TeamGREEN Tech",
    "model": "System2Mqtt"
  },
  "availability": {
    "topic": "system2mqtt/MyServer/LWT",
    "payload_available": "online",
    "payload_not_available": "offline"
  },
  "unit_of_measurement": "%",
  "icon": "mdi:cpu-64-bit",
  "device_class": "power_factor"
}
```

---

## Removing Entities

Discovery configurations are published with the **retain** flag. To remove an entity from Home Assistant, publish an empty (`""`) retained message to its discovery topic:

```sh
mosquitto_pub -h 192.168.1.100 -r -t "homeassistant/sensor/s2m_myserver_cpu/config" -m ""
```

Alternatively, you can remove the device entirely from the Home Assistant MQTT integration UI under **Settings → Devices & Services → MQTT → Devices**.
