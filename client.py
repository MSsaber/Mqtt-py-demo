# !/usr/bin/env python
#-*- encoding : utf-8 -*-

import random,time
from enum import Enum
from paho.mqtt import client as mqtt_client
from threading import Thread, Lock

#
class MqttClientType(Enum):
    pub = 'publish'
    sub = 'subscribe'
    both = 'all'

#
class MqttClient(object):
    _callback_name = [ 'on_connect', 'on_connect_fail', 'on_disconnect', 'on_message', 'on_publish',
                    'on_subscribe', 'on_unsubscribe', 'on_log', 'on_socket_open', 'on_socket_close',
                    'on_socket_register_write', 'on_socket_unregister_write' ]
    def __init__(self, type : MqttClientType, broker, port, **kwargs):
        self.callbacks = kwargs
        self.type = type
        self.broker = broker
        self.port = port
        self._client = None
        self._client_id = f'test-device-{random.randint(0, 1000)}'

        """
        """
        self._pub_lock = Lock()
        self._sub_lock = Lock()
        self._pub_run = True
        self._sub_run = False

        self._pub_thread = None
        self._sub_thread = None

    def CID(self):
        return self._client_id

    def initial(self):
        self._client = mqtt_client.Client(self._client_id)
        """
        """
        for k,v in self.callbacks.items():
            key = "_" + k
            if k in MqttClient._callback_name and\
                key in self._client.__dict__.keys():
                self._client.__dict__[key] = v
        self._client.connect(self.broker, self.port)

    def start(self):
        self._client.loop_start()

    def stop(self):
        self._client.loop_stop()

    def publish(self, topic, msg):
        pub_msg = f"messages: {msg}"
        result = self._client.publish(topic, msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")

    def _loop_publish(self):
        while self._pub_run:
            self._pub_lock.acquire()
            time.sleep(self._gap)
            self.publish(self._topic, self._msg)
            self._pub_lock.release()

    def loop_publish(self, topic, msg, gap):
        self._gap = gap
        self._msg = msg
        self._topic = topic
        self._pub_thread = Thread(target=self._loop_publish)
        self._pub_thread.start()

    def close_publish(self):
        self._pub_lock.acquire()
        self._pub_run = False
        self._pub_lock.release()

    def subscribe(self, topic):
        self._client.subscribe(topic)

    def unsubscribe(self, topic):
        self._client.unsubscribe(topic)

    def loop_forever(self):
        self._client.loop_forever()
        