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
    '''
    显示成功链接至broker的信息
    '''
    def on_connect(client, userdata, flags, rc):
        print('userdata : %s' % (userdata))
        if rc == 0:
            print("Connected to MQTT Broker! Publisher working...")
        else:
            print("Failed to connect with error %d\n", rc)

class Publish2(Publish):
    '''
    订阅信息回调
    '''
    def on_message(client, userdata, msg):
        '''
        设备3会在用户设置的计数达到后取消对设备2消息的订阅
        '''
        global moniter_count
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        parse_msg = msg.payload.decode().split(':')
        if len(parse_msg) < 2: return
        if int(parse_msg[1]) >= moniter_count:
            publish3.unsubscribe(topic2)
            print('Device3 subscribe over!')


class Publish3(Publish2):
    '''
    订阅状态回调
    '''
    def on_subscribe(client, userdata, mid, granted_qos):
        print(f"Subscribe status : ",userdata,mid,granted_qos)

def create_publisher(id):
    global publish1,publish2,publish3
    if id == 1:
        '''
        设备1,仅发布设备运行正常信息
        '''
        publish1 = MqttClient(MqttClientType.pub, broker, port, \
            on_connect = Publish.on_connect)
        publish1.initial()
        publish1.start()
        publish1.loop_publish(topic1, 'Device1 status ok...', 1)
    elif id == 2:
        '''
        设备2,模拟设备状态变化的消息发布
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
        设备3,模拟设备状态变化的消息发布,并且会接收设备2的状态信息,在达到模拟状态后会取消对设备2消息的订阅
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
    通过配置参数选择需要启动的设备
    e.g. python3 publish.py --pub 1
         python3 publish.py --pub 2
         python3 publish.py --pub 3 --count 40
         count 参数设置设备3监听变化的参数
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