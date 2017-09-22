# -*- coding: utf-8 -*-
"""
Created on Sat Jan 14 16:19:30 2017

@author: Feng-cong Li
"""
import socket
import random
import struct
import json
import datetime
import importlib

from pathlib import Path

import qrcode
from PIL import ImageTk

import six.moves.tkinter as tk
import six.moves.tkinter_ttk as ttk
from wavesynlib.toolwindows.tkbasewindow import TkToolWindow
from wavesynlib.guicomponents.tk import json_to_tk, ScrolledCanvas, ScrolledText, LabeledEntry
from wavesynlib.languagecenter.wavesynscript import Scripting, code_printer
from wavesynlib.languagecenter.utils import get_caller_dir, call_immediately



_plugins = {'location':[]}



@call_immediately
def load_plugins():
    self_dir = Path(get_caller_dir())
    loc_dir = self_dir.joinpath('plugins/locationsensor')
    for file in loc_dir.glob('*.py'):
        if file.name == '__init__.py':
            continue
        mod_name = file.name[:-3] # Remove the suffix ".py" which has three chars.
        mod_path = f'wavesynlib.toolwindows.mobiledevice.plugins.locationsensor.{mod_name}'
        mod = importlib.import_module(mod_path)
        _plugins['location'].append(mod.Plugin(Scripting.root_node))
        


class DataTransferWindow(TkToolWindow):
    window_name = 'WaveSyn-DataTransfer'
    _qr_tab = 0
    _data_tab = 1
    
    def __init__(self):
        '''Structure of command:
action: read / write

if action == "read":
    source = clipboard / location_sensor / album
'''
        TkToolWindow.__init__(self)
        self._gui_images = []
        tool_tabs = self._tool_tabs
        
        default_qr_size = 200
        
        widgets_desc = [
{'class':'Group', 'pack':{'side':'left', 'fill':'y'}, 'setattr':{'name':'Clipboard'}, 'children':[
    {'class':'Button', 'name':'read_clipb', 
         'balloonmsg':'Read the clipboard of an Android device.',
         'config':{'text':'Read', 'command':self.__on_read_device_clipboard}},
    {'class':'Button', 'name':'write_clipb', 
         'balloonmsg':'Write the clipboard of an Android device.',
         'config':{'text':'Write', 'command':lambda:self._launch_server({'direction':'to device', 'data_type':'text', 'clipboard':True})}} # To Do: Change it. 
]},

{'class':'Group', 'pack':{'side':'left', 'fill':'y'}, 'setattr':{'name':'Sensors'}, 'children':[
    {'class':'Button', 
         'balloonmsg':'Read the AGPS sensor of an Android device.',
         'config':{'text':'Location', 'command':self.__on_read_device_location}}
]},

{'class':'Group', 'pack':{'side':'left', 'fill':'y'}, 'setattr':{'name':'QR Code'}, 'children':[
    {'class':'LabeledEntry', 'name':'qr_size', 
         'balloonmsg':'Size (pixels) of the generated QR code.',
         'setattr':{
             'label_text':'Size', 
             'label_width':5, 
             'entry_width':8,
             'entry_text':str(default_qr_size),
             'checker_function':self.root_node.gui.value_checker.check_int}},
    {'class':'Button', 'config':{'text':'Ok'}}
]}
]

        balloon = self.root_node.gui.balloon
        tab = tk.Frame(tool_tabs)
        self.__widgets = widgets = json_to_tk(tab, widgets_desc, balloon=balloon)
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
        scrolled_text.auto_url_link = True
        
        def on_url_link_click(url):
            with code_printer():
                self.root_node.webbrowser_open(url)
                
        scrolled_text.on_url_link_click = on_url_link_click
        
        data_book.add(scrolled_text, text='Text')
        
        data_book.pack(expand='yes', fill='both')
        
        self._make_window_manager_tab()
        
        
    @property
    def qr_size(self):
        return int(self.__widgets['qr_size'].entry_text)
        
        
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
        image = qrcode.make(qr_string).resize((self.qr_size, self.qr_size))        
        self.__qr_image = ImageTk.PhotoImage(image=image) 
 
        if self.__qr_id is None:
            self.__qr_id = self.__qr_canvas.canvas.create_image((0, 0), image=self.__qr_image, anchor='nw')
        else:
            self.__qr_canvas.canvas.itemconfig(self.__qr_id, image=self.__qr_image) 
        self.__data_book.select(self._qr_tab)
            
        @self.root_node.thread_manager.new_thread_do
        def transfer():
            with sockobj:
                sockobj.listen(2)
                # Here it waits for two potential objects.
                # One is the android data provider,
                # and the other is WaveSyn itself for cancellation.
                #
                # If the data receiving mission is aborted for some reason,
                # the main threa of WaveSyn will send a piece of data here,
                # to notify this thread not to wait any longer. 
                #
                # The first byte of the received data is the exit_flag.
                # If WaveSyn wants to abort this data receiving mission, 
                # it will send a byte exit_flag='0x00', and this thread kills itself.
                #
                # Data format:
                # [exit_flag:1byte] [password:4bytes] [data:arbitrary bytes]
                
                conn, addr = sockobj.accept()
                
                @self.root_node.thread_manager.main_thread_do(block=False)
                def clear_qr_image():
                    self.__qr_canvas.canvas.delete(self.__qr_id)
                    self.__qr_id = None
        
                exit_flag = conn.recv(1)
                if exit_flag != b'\x00':
                    # The first byte is zero, which means abort this transfer mission.
                    return
                
                password = struct.unpack('!I', conn.recv(4))[0]
                if password != self.__password:
                    return
                    
                if command['action'] == 'read':
                    # Loop receiving data
                    data_list = []
                    while True:
                        data = conn.recv(8192)
                        if not data: 
                            break
                        data_list.append(data)
                    data = b''.join(data_list)
                    # End receiving data            
                    
                    if command['source'] in ('clipboard', 'location_sensor'):
                        # Store received data
                        text = data.decode('utf-8')
                        self.__data = {'data':text, 'type':'text'}
                        # End store received data
                        
                        if command['source'] == 'location_sensor':
                            pos = json.loads(text)                    
                            text = f'latitude={pos["latitude"]}, longitude={pos["longitude"]}'
                        
                        @self.root_node.thread_manager.main_thread_do(block=False)
                        def show_text():
                            # Always manipulate the GUI components in the main thread!
                            scrolled_text = self.__scrolled_text
                            scrolled_text.append_text(text)
                            scrolled_text.append_text('\n\n')
                            
                            # Generate Copy Link
                            def copy_link_action(dumb):
                                self.root_node.interfaces.os.clipboard.write(text)
                                
                            tag_name = scrolled_text.create_link_tag(copy_link_action)
                            scrolled_text.append_text('[COPY]', tag_name)
                            scrolled_text.append_text(' ')
                            # End Generate Copy Link
                            
                            # Generate Plugin Links
                            if command['source'] == 'location_sensor':
                                for plugin in _plugins['location']:
                                    if not plugin.test_data(pos):
                                        continue
                                    def link_action(dumb, plugin=plugin):
                                        plugin.action(pos)
                                    tag_name = scrolled_text.create_link_tag(link_action)
                                    scrolled_text.append_text(f'[{plugin.link_text}]', tag_name)
                                    scrolled_text.append_text(' ')
                            # End Generate Plugin Links
                            
                            scrolled_text.append_text('\n{}{}{}\n\n\n'.format(
                                '='*12, 
                                datetime.datetime.now().isoformat(), 
                                '='*12
                            ))
                            
                            
                    @self.root_node.thread_manager.main_thread_do(block=False)
                    def on_finish():
                        # Always manipulate the GUI components in the main thread.
                        self.__data_book.select(self._data_tab)
                        if self.__on_finish:
                            self.__on_finish(self.device_data['data'])
                            self.__on_finish = None        
    
    
    @Scripting.printable
    def read_device_clipboard(self, on_finish):
        self._launch_server(command={'action':'read', 'source':'clipboard'})
        self.__on_finish = on_finish
        
        
    @Scripting.printable
    def read_device_location(self, on_finish):
        self._launch_server(command={'action':'read', 'source':'location_sensor'})
        self.__on_finish = on_finish
        
        
    def __on_read_device_clipboard(self, on_finish=None):
        with code_printer():
            self.read_device_clipboard(on_finish=on_finish)
            
            
    def __on_read_device_location(self, on_finish=None):
        with code_printer():
            self.read_device_location(on_finish=on_finish)
    
    
    def _clipb_to_dev(self):
        pass