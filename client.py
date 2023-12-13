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
    '''
    MQTT的客户端封装类,可以做为发布者,订阅者和收发者
    '''
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
        self._pub_run = True
        self._sub_run = False

        self._pub_thread = None

    def CID(self):
        '''
        获取客户端ID号
        '''
        return self._client_id

    def initial(self):
        '''
        初始化客户端配置,主要配置broker和连接端口.并且会将设置的回调函数通过
        Mqtt.Client的__dict__的key检测配置给实例
        '''
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
        '''
        消息发布: 1.topic主题 2.msg消息
        '''
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
        '''
        固定消息的循环发布: 1.topic主题 2.msg消息 3.gap发布间隔
        '''
        self._gap = gap
        self._msg = msg
        self._topic = topic
        self._pub_thread = Thread(target=self._loop_publish)
        self._pub_thread.start()

    def close_publish(self):
        '''
        关闭固定循环发布
        '''
        self._pub_lock.acquire()
        self._pub_run = False
        self._pub_lock.release()

    def subscribe(self, topic):
        '''
        订阅:topic需要订阅的主题
        '''
        self._client.subscribe(topic)

    def unsubscribe(self, topic):
        '''
        取消订阅:topic需要取消订阅的主题
        '''
        self._client.unsubscribe(topic)

    def loop_forever(self):
        self._client.loop_forever()
        