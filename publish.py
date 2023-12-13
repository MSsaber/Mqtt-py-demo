# !/usr/bin/env python
#-*- encoding : utf-8 -*-

import time
from client import *

publish1 = None
publish2 = None
publish3 = None

broker = 'broker.emqx.io'
port = 1883
topic1 = "/python/mqtt/pub1"
topic2 = "/python/mqtt/pub2"
topic3 = "/python/mqtt/pub3"

moniter_count = 30

class Publish:
    def on_connect(client, userdata, flags, rc):
        print('userdata : %s' % (userdata))
        if rc == 0:
            print("Connected to MQTT Broker! Publisher working...")
        else:
            print("Failed to connect with error %d\n", rc)

class Publish2(Publish):
    def on_message(client, userdata, msg):
        global moniter_count
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        parse_msg = msg.payload.decode().split(':')
        if len(parse_msg) < 2: return
        if int(parse_msg[1]) >= moniter_count:
            publish3.unsubscribe(topic2)
            print('Device3 subscribe over!')


class Publish3(Publish2):
    def on_subscribe(client, userdata, mid, granted_qos):
        print(f"Subscribe status : ",userdata,mid,granted_qos)

def create_publisher(id):
    global publish1,publish2,publish3
    if id == 1:
        '''
        '''
        publish1 = MqttClient(MqttClientType.pub, broker, port, \
            on_connect = Publish.on_connect)
        publish1.initial()
        publish1.start()
        publish1.loop_publish(topic1, 'Device1 status ok...', 1)
    elif id == 2:
        '''
        '''
        publish2 = MqttClient(MqttClientType.pub, broker, port, \
        on_connect = Publish2.on_connect, on_message = Publish2.on_message)
        publish2.initial()
        publish2.start()
        num = 0
        while True:
            time.sleep(1)
            publish2.publish(topic2, 'Device-count:%d' % (num))
            num+=1
    elif id == 3:
        '''
        '''
        publish3 = MqttClient(MqttClientType.both, broker, port, \
        on_connect = Publish3.on_connect, on_subscribe = Publish3.on_subscribe,\
        on_message = Publish3.on_message)
        publish3.initial()
        publish3.subscribe(topic2)
        publish3.start()
        num = 0
        while True:
            time.sleep(1)
            publish3.publish(topic3, 'Device-count:%d' % (num))
            num+=1

if __name__ == '__main__':
    import argparse
    '''
    '''
    args_parse = argparse.ArgumentParser()
    args_parse.add_argument('--pub',type=int)
    args_parse.add_argument('--count',type=int)
    args = args_parse.parse_args()
    if args.pub > 3:
        print('Invalid device id')
    if args.count is not None:
        moniter_count = args.count
    create_publisher(args.pub)