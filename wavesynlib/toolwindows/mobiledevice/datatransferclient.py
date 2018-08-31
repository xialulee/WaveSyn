# -*- coding: utf-8 -*-
#qpy:kivy	
"""
Created on Sat Jan 14 19:38:45 2017

@author: Feng-cong Li
"""
MAXDEVCODELEN = 32



if __name__ == '__main__':
    import socket
    import json
    import struct
    import time
    import os
    import urllib
    import tempfile
    
    import androidhelper
    from jnius import autoclass
    from android import mActivity
    
    droid = androidhelper.Android()
    Build = autoclass('android.os.Build') 
    Media = autoclass('android.provider.MediaStore$Images$Media')
    Environment = autoclass('android.os.Environment')
    
    
    _device_code = '{} {}'.format(Build.MANUFACTURER, Build.MODEL)
    _device_code += '\x00'*MAXDEVCODELEN
    _device_code = _device_code[:MAXDEVCODELEN]
    
    
    
    def init_and_send_head(ip, port, password, datalen):
        sockobj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockobj.connect((ip, port))
        sockobj.send('\x00') # Exit Flag
        sockobj.send(struct.pack('!I', password))
        sockobj.send(_device_code) # Device Code
        sockobj.send(struct.pack('!I', datalen))
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
        data = {'data':text}
        data = json.dumps(data)
        sockobj = init_and_send_head(ip, port, password, len(data))
        sockobj.send(data)
        sockobj.close()
        
        
        
    def send_clipb_text(ip, port, password):
        text = droid.getClipboard().result.encode('utf-8')
        send_text(text, ip, port, password)
        
        
        
    def recv_text(ip, port, password):
        sockobj = init_and_send_head(ip, port, password, 0)
        
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
        result = droid.startActivityForResult('android.intent.action.PICK', type='image/*')
        uri = result.result['data']
        result = droid.queryContent(uri)
        path = result.result[0]['_data']
        return path
    
    
    
    def send_photo(path, ip, port, password):
        path = path.encode('utf-8') 
        with open(path, 'rb') as image_file:
            data = image_file.read()
            sockobj = init_and_send_head(ip, port, password, datalen=len(data))
            sockobj.send(data)
            
            
            
    def pick_and_send_photo(ip, port, password):
        path = pick_photo()
        send_photo(path, ip, port, password)
        
        
        
    def pick_file():
        result = droid.startActivityForResult('android.intent.action.GET_CONTENT', type='file/*')
        path = result.result['data']
        if path[:7] == 'file://':
            path = urllib.unquote_plus(path.encode('utf-8'))[7:]
        else:
            path = droid.queryContent(path).result[0]['_data'].encode('utf-8')
        return path
    
    
    
    def send_file(path, ip, port, password):
        #path = path.encode('utf-8')
        with open(path, 'rb') as f:
            sockobj = init_and_send_head(ip, port, password, datalen=os.path.getsize(path))
            filename = os.path.split(path)[1]
            sockobj.send(chr(len(filename)))
            sockobj.send(filename)
            while True:
                buf = f.read(32768)
                if not buf:
                    break
                sockobj.send(buf)
            
        
        
    def pick_and_send_file(ip, port, password):
        path = pick_file()
        send_file(path, ip, port, password)
        
        
        
    def view_photo(path):
        uri = Media.insertImage(mActivity.getContentResolver(), path, None, None)
        droid.view(str(uri))
        
        
        
    def get_download_path():
        return str(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS).getPath())
        
        
        
    def recv_file(dir_, name, ip, port, password):
        def recv_data(f):
            sockobj = init_and_send_head(ip, port, password, 0)
            while True:
                buf = sockobj.recv(32768)
                if not buf:
                    break
                f.write(buf)
            f.flush() # Important! Make sure "view_photo" can get a flushed image file.
            sockobj.close()        
        
        name = name.encode('utf-8')
        
        ext = os.path.splitext(name)[-1].lower()
        if ext in ('.jpg', '.jpeg', '.png', '.gif'):
            with tempfile.NamedTemporaryFile(suffix=ext) as f:
                recv_data(f)
                view_photo(f.name)
        else:
            download_path = get_download_path()
            name_cnt = 0
            while True:
                file_path = os.path.join(download_path, '[{}]{}'.format(name_cnt, name))
                if not os.path.exists(file_path):
                    break
                name_cnt += 1  
            with open(file_path, 'wb') as f:
                recv_data(f)
        
    
    
    ip, port, password, command = read_qr()
    action = command[u'action']
    if action == u'read':
        {'clipboard':       send_clipb_text,
         'location_sensor': send_location_json,
         'gallery': pick_and_send_photo,
         'storage': pick_and_send_file
        }[command['source']](ip, port, password)
    elif action == u'write':
        if command['target'] == 'clipboard':
            recv_clipb_text(ip, port, password)
        elif command['target'][:4] == 'dir:':
            name = command['name']
            dir_ = command['target'][4:]
            recv_file(dir_, name, ip, port, password)
