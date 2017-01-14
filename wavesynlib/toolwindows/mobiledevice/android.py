# -*- coding: utf-8 -*-
"""
Created on Sat Jan 14 16:19:30 2017

@author: Feng-cong Li
"""
from __future__ import print_function, division, unicode_literals

import socket
import random
import struct
import json
import thread
import threading

import qrcode
from PIL import ImageTk

import six.moves.tkinter as tk
import six.moves.tkinter_ttk as ttk
from wavesynlib.toolwindows.basewindow import TkToolWindow
from wavesynlib.guicomponents.tk import json_to_tk, ScrolledCanvas
from wavesynlib.interfaces.timer.tk import TkTimer

class DataTransferWindow(TkToolWindow):
    window_name = 'WaveSyn-DataTransfer'
    
    def __init__(self):
        '''Structure of command:
direction: from device / to device
data_type: text / image
'''
        TkToolWindow.__init__(self)
        self._gui_images = []
        tool_tabs = self._tool_tabs
        
        widgets_desc = [
{'class':'Group', 'pack':{'side':'left', 'fill':'y'}, 'setattr':{'name':'Clipboard Sync'}, 'children':[
    {'class':'Button', 'config':{'text':'From Dev', 'command':lambda:self._launch_server({'direction':'from device', 'data_type':'text', 'clipboard':True})}},
    {'class':'Button', 'config':{'text':'To Dev', 'command':lambda:self._launch_server({'direction':'to device', 'data_type':'text', 'clipboard':True})}}
]}
]

        tab = tk.Frame(tool_tabs)
        widgets = json_to_tk(tab, widgets_desc)
        tool_tabs.add(tab, text='Data')
        
        tk_object = self.tk_object        
        data_book = ttk.Notebook(tk_object)
        
        self.__qr_canvas = qr_canvas = ScrolledCanvas(data_book) 
        self.__qr_image = None
        self.__qr_id = None
        self.__password = None
        self.__data = None
        self.__finish_event = threading.Event()

        self.__timer = TkTimer(self, interval=100)
        self.__timer.active = False
        self.__timer.add_observer
        def observer():
            pass

        data_book.add(qr_canvas, text='QR Code')
        data_book.pack(expand='yes', fill='both')
        
        self._make_window_manager_tab()
        
        
    @property
    def data(self):
        return self.__data
        
        
    def _launch_server(self, command):
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

        self_ip = socket.gethostbyname(socket.gethostname())
        self_port = port
        self.__password = password = random.randint(0, 65535)
        qr_string = json.dumps({'ip':self_ip, 'port':self_port, 'password':password, 'command':command})
        image = qrcode.make(qr_string)  
        self.__qr_image = ImageTk.PhotoImage(image=image) 
        #self.__qr_canvas.canvas.config(scrollregion=(0, 0, width, height))   
        if self.__qr_id is None:
            self.__qr_id = self.__qr_canvas.canvas.create_image((0, 0), image=self.__qr_image, anchor='nw')
        else:
            self.__qr_canvas.canvas.itemconfig(self.__qr_id, image=self.__qr_image)  
            
        thread.start_new_thread(self._server_thread, (sockobj, command))
        self.__finish_event.clear()
    
    
    def _server_thread(self, sockobj, command):
        sockobj.listen(2)
        conn, addr = sockobj.accept()

        exit_flag = conn.recv(1)
        if exit_flag != b'\x00':
            return
        password = struct.unpack('!I', conn.recv(4))[0]
        if password != self.__password:
            return
            
        if command['direction'] == 'from device':
            data_list = []
            while True:
                data = conn.recv(8192)
                if not data: 
                    break
                data_list.append(data)
            data = b''.join(data_list)
            if command['data_type'] == 'text':
                self.__data = data.decode('utf-8')
            self.__finish_event.set()
        
        
    def _clipb_from_dev(self):
        pass
    
    
    def _clipb_to_dev(self):
        pass