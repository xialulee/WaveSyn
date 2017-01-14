# -*- coding: utf-8 -*-
"""
Created on Sat Jan 14 19:38:45 2017

@author: Feng-cong Li
"""

import socket
import json
import struct
import androidhelper

droid = androidhelper.Android()

def read_qr():
    result = droid.startActivityForResult('com.google.zxing.client.android.SCAN', extras={'SAVE_HISTORY':False})
    data = json.loads(result.result['extras']['SCAN_RESULT'])
    ip = data['ip']
    port = data['port']
    password = data['password']
    command = data['command']
    return ip, port, password, command

def send_clipb_text(ip, port, password):
    text = droid.getClipboard().result.encode('utf-8')
    sockobj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockobj.connect((ip, port))
    sockobj.send('\x00')
    sockobj.send(struct.pack('!I', password))
    sockobj.send(text)
    sockobj.close()

if __name__ == '__main__':
    ip, port, password, command = read_qr()
    if command[u'direction'] == u'from device' and \
        command[u'clipboard'] is True:
        send_clipb_text(ip, port, password)