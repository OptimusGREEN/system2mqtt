import logging
import json

def get_config_attributes(topic_slug):
    output = {}
    if topic_slug == "/disks/mount/":
        ha_type = "binary_sensor"
        ha_class = "connectivity"
        ha_icon = "None"
        ha_unit = "None"
    elif topic_slug == "/disks/storage/":
        ha_type = "sensor"
        ha_icon = "mdi:harddisk"
        ha_unit = "%"
        ha_class ="None"
    elif topic_slug == "/cpu/temperature" or "/disks/temperature":
        ha_type = "sensor"
        ha_class = "temperature"
        ha_icon = "mdi:thermometer"
        ha_unit = "°C"
    elif topic_slug == "/cpu/usage":
        ha_type = "sensor"
        ha_unit = "%"
        ha_icon = "mdi:cpu-64-bit"
        ha_class = "None"
    elif topic_slug == "/memory":
        ha_type = "sensor"
        ha_unit = "%"
        ha_icon = "mdi:memory"
        ha_class = "None"
    elif topic_slug == "/fan_speed":
        ha_type = "sensor"
        ha_unit = "%"
        ha_icon = "mdi:fan"
        ha_class = "None"
    else:
        logging.error("topic slug not recognised")
        ha_type = "None"
        ha_unit = "None"
        ha_icon = "None"
        ha_class = "None"
    output["entity_type"] = ha_type
    output["entity_class"] = ha_class
    output["entity_icon"] = ha_icon
    output["entity_unit"] = ha_unit
    return output

def ha_config(topic_template, topic_slug, name, object_id, state_topic, device,
              availability_topic=None, payload_on=None, payload_off=None, off_delay=None):
    atts = get_config_attributes(topic_slug)
    discovery_topic = topic_template.format(atts.get("entity_type"))
    payload = {
        "name": name,
        "unique_id": object_id,
        "object_id": object_id,
        "state_topic": state_topic,
        "device": {
            "identifiers": device,
            "name": "S2M " + device.title(),
            "manufacturer": "TeamGREEN Tech",
            "model": "System2Mqtt"
        }
    }
    if availability_topic:
        payload["availability_topic"] = availability_topic
    if payload_on:
        payload["payload_on"] = payload_on
    if payload_off:
        payload["payload_off"] = payload_off
    if off_delay:
        payload["off_delay"] = off_delay
    if not atts.get("entity_unit") == "None":
        payload["unit_of_measurement"] = atts.get("entity_unit")
    if not atts.get("entity_icon") == "None":
        payload["icon"] = atts.get("entity_icon")
    if not atts.get("entity_class") == "None":
        payload["device_class"] = atts.get("entity_class")

    config_payload = json.dumps(payload)
    logging.debug("Discovery Topic: {}".format(discovery_topic))
    logging.debug("Discovery Payload: \n{}".format(payload))
    return (discovery_topic, config_payload)