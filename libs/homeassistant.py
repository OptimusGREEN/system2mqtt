import logging
import json

def ha_config(discovery_topic, name, object_id, state_topic, device, entity_type,
              icon=None, device_class=None, unit=None, availability_topic=None,
              payload_available="online", payload_not_available="offline",
              payload_on=None, payload_off=None, off_delay=None):
    """
    Generate Home Assistant MQTT discovery configuration.
    
    Args:
        discovery_topic: MQTT topic for discovery
        name: Entity display name
        object_id: Unique object identifier
        state_topic: Topic where entity state is published
        device: Device identifier
        entity_type: Type of entity (sensor, binary_sensor, etc.)
        icon: Material Design icon (optional)
        device_class: Device class for entity (optional)
        unit: Unit of measurement (optional)
        availability_topic: Topic for availability status (optional)
        payload_available: Payload indicating device is available (default: "online")
        payload_not_available: Payload indicating device is unavailable (default: "offline")
        payload_on: Payload for "on" state (for binary sensors/switches)
        payload_off: Payload for "off" state (for binary sensors/switches)
        off_delay: Delay before switching to off state
    
    Returns:
        tuple: (discovery_topic, config_payload_json)
    """
    logging.debug(f"Creating HA config for entity_type: {entity_type}")
    
    payload = {
        "name": name,
        "unique_id": object_id,
        "object_id": object_id,
        "state_topic": state_topic,
        "device": {
            "identifiers": [device],  # Should be a list
            "name": f"S2M {device.title()}",
            "manufacturer": "TeamGREEN Tech",
            "model": "System2Mqtt"
        }
    }
    
    # Add availability configuration if topic is provided
    if availability_topic:
        payload["availability"] = {
            "topic": availability_topic,
            "payload_available": payload_available,
            "payload_not_available": payload_not_available
        }
    
    # Add entity-specific configurations
    if payload_on:
        payload["payload_on"] = payload_on
    if payload_off:
        payload["payload_off"] = payload_off
    if off_delay:
        payload["off_delay"] = off_delay
    if unit:
        payload["unit_of_measurement"] = unit
    if icon:
        payload["icon"] = icon
    if device_class:
        payload["device_class"] = device_class

    config_payload = json.dumps(payload, indent=2)
    logging.debug(f"Discovery Topic: {discovery_topic}")
    logging.debug(f"Discovery Payload:\n{config_payload}")
    
    return (discovery_topic, config_payload)


# Example usage:
def create_sensor_with_availability():
    """Example of creating a sensor with availability tracking"""
    return ha_config(
        discovery_topic="homeassistant/sensor/s2m_cpu/config",
        name="CPU Usage",
        object_id="s2m_cpu_usage",
        state_topic="s2m/system/cpu",
        device="system_monitor",
        entity_type="sensor",
        icon="mdi:cpu-64-bit",
        device_class="power_factor",
        unit="%",
        availability_topic="s2m/system/status",
        payload_available="online",
        payload_not_available="offline"
    )


# Usage with custom availability payloads:
def create_binary_sensor_custom_availability():
    """Example with custom availability payloads"""
    return ha_config(
        discovery_topic="homeassistant/binary_sensor/s2m_service/config",
        name="Service Status",  
        object_id="s2m_service_status",
        state_topic="s2m/service/state",
        device="service_monitor",
        entity_type="binary_sensor",
        icon="mdi:server",
        device_class="connectivity",
        availability_topic="s2m/service/heartbeat",
        payload_available="alive",      # Custom available payload
        payload_not_available="dead",   # Custom unavailable payload
        payload_on="running",
        payload_off="stopped"
    )