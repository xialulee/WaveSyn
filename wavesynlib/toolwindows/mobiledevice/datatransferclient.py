# -*- coding: utf-8 -*-
"""
Created on Sat Jan 14 19:38:45 2017

@author: Feng-cong Li
"""

import socket
import json
import struct
import time

import androidhelper as android

droid = android.Android()


def read_qr():
    result = droid.startActivityForResult('com.google.zxing.client.android.SCAN', extras={'SAVE_HISTORY':False})
    data = json.loads(result.result['extras']['SCAN_RESULT'])
    ip = data['ip']
    port = data['port']
    password = data['password']
    command = data['command']
    return ip, port, password, command
    
    
def send_text(text, ip, port, password):
    sockobj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockobj.connect((ip, port))
    sockobj.send('\x00')
    sockobj.send(struct.pack('!I', password))
    sockobj.send(text)
    sockobj.close()
    
    
def send_clipb_text(ip, port, password):
    text = droid.getClipboard().result.encode('utf-8')
    send_text(text, ip, port, password)
    
    
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


if __name__ == '__main__':
    ip, port, password, command = read_qr()
    if command[u'direction'] == u'from device':
        if 'clipboard' in command and command[u'clipboard'] is True:
            send_clipb_text(ip, port, password)
        elif 'location' in command and command[u'location'] is True:
            location = get_location()