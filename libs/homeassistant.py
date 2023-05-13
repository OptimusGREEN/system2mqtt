import logging
import json

def ha_config(discovery_topic, name, object_id, state_topic, device, entity_type,
              icon=None, device_class=None, unit=None, availability_topic=None,
              payload_on=None, payload_off=None, off_delay=None):
    logging.debug(entity_type)
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
    if unit:
        payload["unit_of_measurement"] = unit
    if icon:
        payload["icon"] = icon
    if device_class:
        payload["device_class"] = device_class

    config_payload = json.dumps(payload)
    logging.debug("Discovery Topic: {}".format(discovery_topic))
    logging.debug("Discovery Payload: \n{}".format(payload))
    return (discovery_topic, config_payload)