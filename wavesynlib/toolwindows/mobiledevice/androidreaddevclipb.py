# -*- coding: utf-8 -*-
"""
Created on Sun Apr 02 18:51:02 2017

@author: Feng-cong Li
"""

from __future__ import print_function, division, unicode_literals

import socket
import thread
import struct
import random
import json

import androidhelper as android
droid = android.Android()



def task(data):
    # Add your code here
    print(data)
    # End
    
    
    
def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]    



def create_qr(content):
    return droid.startActivityForResult(
        'com.google.zxing.client.android.ENCODE',
        extras={'ENCODE_DATA':content, 'ENCODE_TYPE':'TEXT_TYPE'}
    )



def create_sockobj():
    sockobj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 10000
    while True:
        try:
            sockobj.bind(('', port))
        except socket.error:
            port += 1
            if port > 65535:
                raise socket.error
        else:
            break
    return sockobj, port
    
    
    
def server_thread(sockobj, command, password):
    sockobj.listen(1)
    conn, addr = sockobj.accept()
    conn.recv(1) # exit flag not used here
    received_password = struct.unpack(str('!I'), conn.recv(4))[0]   
    if received_password != password:
        return
        
    if command['action'] == 'read':
        data_list = []
        while True:
            data = conn.recv(8192)
            if not data:
                break
            data_list.append(data)
        data = b''.join(data_list)
        
        text = data.decode('utf-8')
        task(text)



def main():
    sockobj, port = create_sockobj()
    password = random.randint(0, 65535)
    command = {'action':'read', 'source':'clipboard'}
    thread.start_new(server_thread, (sockobj, command, password))
    qr_str = json.dumps({'ip':get_ip_address(), 'port':port, 'password':password, 'command':command})
    create_qr(qr_str)



if __name__ == '__main__':
    main()