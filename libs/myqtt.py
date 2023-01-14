import paho.mqtt.client as mqtt

import logging, time


class Myqtt(object):
    def __init__(self, host, port=1883, username=None, password=None):
        logging.debug("")

        self.host = host
        self.port = port
        self.username = username
        self.password = password

        self.connected_flag = False
        self.topic_callbacks = {}
        self.connected_callback = None

        self.lwt_topic = None
        self.lwt_offline_payload = "offline"
        self.lwt_online_payload = "online"
        self.lwt_retain = True

        self.client = mqtt.Client()

    def run(self):
        logging.debug("{}, {}, {}, {}".format(self.host, self.port, self.username, self.password))
        if self.lwt_topic:
            self.client.will_set(topic=self.lwt_topic, payload=self.lwt_offline_payload, retain=self.lwt_retain)
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)
        self.client.reconnect_delay_set(min_delay=1, max_delay=120)
        logging.info("Attempting to connect to mqtt broker...")
        logging.info("Host: {}".format(self.host))
        logging.info("User: {}".format(self.username))
        self.client.connect_async(self.host, self.port)
        self.client.loop_start()
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.client.on_publish = self.on_publish
        self.client.on_subscribe = self.on_subscribe
        self.client.on_unsubscribe = self.on_unsubscribe
        self.client.on_log = self.on_log

    def publish(self, topic, payload, qos=0, retain=False):
        logging.debug("topic: {}\npayload: {}".format(topic, payload))
        self.client.publish(topic, payload, qos, retain)
        if self.lwt_topic:
            self.client.publish(topic=self.lwt_topic, payload=self.lwt_online_payload, retain=self.lwt_retain)


    #### callbacks ####

    def on_connect(self, client, userdata, flags, rc):
        logging.debug("")
        return_codes = {0: "Connection successful",
                        1: "Connection refused – incorrect protocol version",
                        2: "Connection refused – invalid client identifier",
                        3: "Connection refused – server unavailable",
                        4: "Connection refused – bad username or password",
                        5: "Connection refused – not authorised"}
        if rc==0:
            logging.info("Connection Code: {}".format(return_codes[rc]))
            self.connected_flag = True
            self.subscription_setup()
            if self.lwt_topic:
                self.publish(topic=self.lwt_topic, payload=self.lwt_online_payload, retain=self.lwt_retain)
            else:
                logging.warning("no lwt topic set")
            if self.connected_callback:
                logging.debug("Calling the 'connected_callback'")
                self.connected_callback()
        else:
            logging.error(return_codes[rc])

    def on_disconnect(self, client, userdata, rc):
        logging.warning("Disconnected from broker with code ({})".format(rc))
        self.connected_flag = False

    def on_message(self, client, userdata, message):
        logging.info("\nTOPIC: {}".format(message.topic))
        logging.info("PAYLOAD: {}\n".format(message.payload.decode("utf-8")))

    def on_publish(self, client, userdata, mid):
        logging.debug("Published Message ID: {}".format(mid))

    def on_subscribe(self, client, userdata, mid, granted_qos):
        logging.info("Subscribed: {}".format(mid))

    def on_unsubscribe(self, client, userdata, mid):
        logging.debug("Unsubscribe return code ({})".format(mid))

    def on_log(self, client, userdata, level, buf):
        pass

    def subscription_setup(self):
        logging.info("Setting up subscriptions")
        if self.topic_callbacks:
            for topic, callback in self.topic_callbacks.items():
                self.client.subscribe(topic)
                logging.info("Subscribing to topic: {}".format(topic))
                if callable(callback):
                    logging.info("Adding subscription callback for topic")
                    self.client.message_callback_add(topic, callback)
        else:
            logging.info("No topics to subscribe to.")