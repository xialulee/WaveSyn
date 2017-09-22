# -*- coding: utf-8 -*-
"""
Created on Sat Jan 14 19:38:45 2017

@author: Feng-cong Li
"""

import socket
import json
import struct
import time
import os

import androidhelper as android

droid = android.Android()


MAXDEVCODELEN = 16
_device_code = os.environ['HOSTNAME']
_device_code += '\x00'*MAXDEVCODELEN
_device_code = _device_code[:MAXDEVCODELEN]



def init_and_send_head(ip, port, password):
    sockobj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockobj.connect((ip, port))
    sockobj.send('\x00') # Exit Flag
    sockobj.send(struct.pack('!I', password))
    sockobj.send(_device_code) # Device Code
    return sockobj    



def read_qr():
    result = droid.startActivityForResult('com.google.zxing.client.android.SCAN', extras={'SAVE_HISTORY':False})
    data = json.loads(result.result['extras']['SCAN_RESULT'])
    ip = data['ip']
    port = data['port']
    password = data['password']
    command = data['command']
    return ip, port, password, command

    
    
def send_text(text, ip, port, password):
    sockobj = init_and_send_head(ip, port, password)
    data = {'data':text}
    data = json.dumps(data)
    sockobj.send(data)
    sockobj.close()
    
    
    
def send_clipb_text(ip, port, password):
    text = droid.getClipboard().result.encode('utf-8')
    send_text(text, ip, port, password)
    
    
    
def recv_text(ip, port, password):
    sockobj = init_and_send_head(ip, port, password)
    
    data_list = []
    while True:
        data = sockobj.recv(8192)
        if not data:
            break
        data_list.append(data)
    return json.loads(''.join(data_list).decode('utf-8'))



def recv_clipb_text(ip, port, password):
    data = recv_text(ip, port, password)
    text = data['data']
    droid.setClipboard(text)
    
    
    
def get_location(interval):
    droid.startLocating()
    time.sleep(interval)
    location = droid.readLocation().result
    
    if not location:
        location = droid.getLastKnownLocation()
    
    if 'gps' in location:
        data = location['gps']
    else:
        data = location['network']
        
    return json.dumps({'longitude':data['longitude'], 'latitude':data['latitude']}, indent=2, separators=(',', ': '))
    

    
def send_location_json(ip, port, password, interval=3):
    text = get_location(interval)
    send_text(text, ip, port, password)
    
    
    
def pick_photo():
    # Originally posted on http://blog.sina.com.cn/s/blog_4513dde60102vomu.html
    result = droid.startActivityForResult('android.intent.action.PICK', type='image/')
    uri = result.result['data']
    result = droid.queryContent(uri)
    path = result.result[0]['_data']
    return path



def send_photo(path, ip, port, password):
    with open(path, 'rb') as image_file:
        sockobj = init_and_send_head(ip, port, password)
        sockobj.send(image_file.read())
        
        
        
def pick_and_send_photo(ip, port, password):
    path = pick_photo()
    send_photo(path, ip, port, password)



if __name__ == '__main__':
    ip, port, password, command = read_qr()
    action = command[u'action']
    if action == u'read':
        {'clipboard':       send_clipb_text,
         'location_sensor': send_location_json,
         'gallery': pick_and_send_photo
        }[command['source']](ip, port, password)
    elif action == u'write':
        if command['target'] == 'clipboard':
            recv_clipb_text(ip, port, password)
