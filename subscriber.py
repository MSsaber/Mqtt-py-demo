# !/usr/bin/env python
#-*- encoding : utf-8 -*-

import time
from client import *

subscriber1 = None
subscriber2 = None

broker = 'broker.emqx.io'
port = 1883
topic1 = "/python/mqtt/pub1"
topic2 = "/python/mqtt/pub2"
topic3 = "/python/mqtt/pub3"
topic4 = "/python/mqtt/pub4"

moniter_count = 30

class Subscriber:
    '''
    设备4订阅回调
    '''
    def on_connect(client, userdata, flags, rc):
        print('userdata : %s' % (userdata))
        if rc == 0:
            print("Connected to MQTT Broker! Subscriber working...")
        else:
            print("Failed to connect with error %d\n", rc)

    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

class Subscriber2(Subscriber):
    '''
    设备5订阅回调
    '''
    def on_message(client, userdata, msg):
        '''
        设备5会在达到对设备3的运行消息的监听要求后,切换订阅设备,将订阅设备1与设备2
        '''
        global moniter_count
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        parse_msg = msg.payload.decode().split(':')
        if len(parse_msg) < 2: return
        if int(parse_msg[1]) >= moniter_count:
            subscriber2.unsubscribe(topic3)
            print('Subscribe from all subscribers ...')
            subscriber2.subscribe(topic1)
            subscriber2.subscribe(topic2)
            subscriber2.start()

    def on_subscribe(client, userdata, mid, granted_qos):
        print(f"Subscribe status : ",userdata,mid,granted_qos)

def create_subscriber(id):
    global subscriber1,subscriber2
    if id == 4:
        '''
        设备4,设备4仅订阅设备1运行信息
        '''
        subscriber1 = MqttClient(MqttClientType.sub, broker, port, \
            on_connect = Subscriber.on_connect, on_message=Subscriber.on_message)
        subscriber1.initial()
        subscriber1.subscribe(topic1)
        subscriber1.subscribe(topic2)
        subscriber1.loop_forever()
    elif id == 5:
        '''
        设备5,设备5发布运行信息,并且会根据设备3的运行信息切换订阅设备
        '''
        subscriber2 = MqttClient(MqttClientType.both, broker, port, \
        on_connect = Subscriber2.on_connect, on_message = Subscriber2.on_message,\
        on_subscribe = Subscriber2.on_subscribe)
        subscriber2.initial()
        subscriber2.subscribe(topic3)
        subscriber2.start()
        num = 0
        while True:
            time.sleep(1)
            subscriber2.publish(topic4, 'Device-count:%d' % (num))
            num+=1

if __name__ == '__main__':
    import argparse
    '''
    通过配置参数选择需要启动的设备
    e.g. python3 subscriber.py --sub 4
         python3 subscriber.py --sub 5 --count 60
         count 参数设置设备5监听变化的参数
    '''
    args_parse = argparse.ArgumentParser()
    args_parse.add_argument('--sub',type=int)
    args_parse.add_argument('--count',type=int)
    args = args_parse.parse_args()
    if args.sub != 4 and args.sub != 5:
        print('Invalid device id')
    if args.count is not None:
        moniter_count = args.count
    create_subscriber(args.sub)