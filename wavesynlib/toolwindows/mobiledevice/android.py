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
import datetime
import six.moves._thread as thread

import qrcode
from PIL import ImageTk

import six.moves.tkinter as tk
import six.moves.tkinter_ttk as ttk
from wavesynlib.toolwindows.basewindow import TkToolWindow
from wavesynlib.guicomponents.tk import json_to_tk, ScrolledCanvas, ScrolledText
from wavesynlib.languagecenter.wavesynscript import Scripting, code_printer

class DataTransferWindow(TkToolWindow):
    window_name = 'WaveSyn-DataTransfer'
    _qr_tab = 0
    _data_tab = 1
    
    def __init__(self):
        '''Structure of command:
direction: from device / to device
data_type: text / image
'''
        TkToolWindow.__init__(self)
        self._gui_images = []
        tool_tabs = self._tool_tabs
        
        widgets_desc = [
{'class':'Group', 'pack':{'side':'left', 'fill':'y'}, 'setattr':{'name':'Clipboard'}, 'children':[
    {'class':'Button', 'config':{'text':'Read', 'command':self.__on_read_device_clipboard}},
    {'class':'Button', 'config':{'text':'Write', 'command':lambda:self._launch_server({'direction':'to device', 'data_type':'text', 'clipboard':True})}}
]}
]

        tab = tk.Frame(tool_tabs)
        widgets = json_to_tk(tab, widgets_desc)
        tool_tabs.add(tab, text='Data')
        
        tk_object = self.tk_object        
        self.__data_book = data_book = ttk.Notebook(tk_object)
        
        self.__qr_canvas = qr_canvas = ScrolledCanvas(data_book) 
        self.__qr_image = None
        self.__qr_id = None
        self.__password = None
        self.__data = None
        self.__on_finish = None

        data_book.add(qr_canvas, text='QR Code')
        
        self.__scrolled_text = scrolled_text = ScrolledText(data_book)
        scrolled_text.disable_keys = True
        data_book.add(scrolled_text, text='Text')
        
        data_book.pack(expand='yes', fill='both')
        
        self._make_window_manager_tab()
        
        
    @property
    def device_data(self):
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
        self.__data_book.select(self._qr_tab)
            
        thread.start_new_thread(self._server_thread, (sockobj, command))
    
    
    def _server_thread(self, sockobj, command):
        sockobj.listen(2)
        conn, addr = sockobj.accept()
        
        @self.root_node.main_thread_do(block=False)
        def clear_qr_image():
            self.__qr_canvas.canvas.delete(self.__qr_id)
            self.__qr_id = None

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
                text = data.decode('utf-8')
                self.__data = {'data':text, 'type':'text'}
                
                @self.root_node.main_thread_do(block=False)
                def show_text():
                    scrolled_text = self.__scrolled_text
                    scrolled_text.append_text(text)
                    scrolled_text.append_text('\n\n')
                    
                    # Generate Copy Link
                    def copy_link_action(dumb):
                        self.root_node.interfaces.os.clipboard.write(text)
                        
                    tag_name = scrolled_text.create_link_tag(copy_link_action)
                    scrolled_text.append_text('[COPY] ', tag_name)
                    # End Generate Copy Link
                    
                    scrolled_text.append_text('\n{}{}{}\n\n\n'.format(
                        '='*12, 
                        datetime.datetime.now().isoformat(), 
                        '='*12
                    ))
                    
                    
            @self.root_node.main_thread_do(block=False)
            def on_finish():
                self.__data_book.select(self._data_tab)
                if self.__on_finish:
                    self.__on_finish(self.device_data['data'])
                    self.__on_finish = None
                    
        
    
    @Scripting.printable
    def read_device_clipboard(self, on_finish):
        self._launch_server({'direction':'from device', 'data_type':'text', 'clipboard':True})
        self.__on_finish = on_finish
        
        
    def __on_read_device_clipboard(self, on_finish=None):
        with code_printer:
            self.read_device_clipboard(on_finish=on_finish)
    
    
    def _clipb_to_dev(self):
        pass