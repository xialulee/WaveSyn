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
from io import BytesIO
from threading import Lock

import qrcode
from PIL import ImageTk, Image

import tkinter as tk
import tkinter.ttk as ttk
from wavesynlib.toolwindows.tkbasewindow import TkToolWindow
from wavesynlib.guicomponents.tk import json_to_tk, ScrolledCanvas, ScrolledText, LabeledEntry, PILImageFrame
from wavesynlib.languagecenter.wavesynscript import Scripting, code_printer
from wavesynlib.languagecenter.utils import get_caller_dir, call_immediately



_plugins = {'locationsensor':[], 'file':[], 'text':[]}
MAXDEVCODELEN = 16



@call_immediately
def load_plugins():
    self_dir = Path(get_caller_dir())
    for name, path in [
            ('locationsensor', 'plugins/locationsensor'),
            ('file', 'plugins/file'),
            ('text', 'plugins/text')]:
        loc_dir = self_dir/path
        for file in loc_dir.glob('*.py'):
            if file.name == '__init__.py':
                continue
            mod_name = file.name[:-3] # Remove the suffix ".py" which has three chars.
            mod_path = f'wavesynlib.toolwindows.mobiledevice.plugins.{name}.{mod_name}'
            mod = importlib.import_module(mod_path)
            _plugins[name].append(mod.Plugin(Scripting.root_node))
        


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
        super().__init__()
        
        self._gui_images = []

        res_dir = get_caller_dir()/'resources'
        image_read_clipb = ImageTk.PhotoImage(file=res_dir/'readclipb.png')
        image_write_clipb = ImageTk.PhotoImage(file=res_dir/'writeclipb.png')
        image_get_file = ImageTk.PhotoImage(file=res_dir/'getfile.png')
        image_get_image = ImageTk.PhotoImage(file=res_dir/'getimage.png')
        image_sensor_location = ImageTk.PhotoImage(file=res_dir/'locationsensor.png')
        self._gui_images.extend((image_read_clipb, image_write_clipb, image_get_file, image_get_image, image_sensor_location))
        
        tool_tabs = self._tool_tabs
        
        default_qr_size = 200
        
        widgets_desc = [
{'class':'Group', 'pack':{'side':'left', 'fill':'y'}, 'setattr':{'name':'Clipboard'}, 'children':[
    {'class':'Button', 'name':'read_clipb', 
         'balloonmsg':'Read the clipboard of an Android device.',
         'config':{'text':'Read', 'image':image_read_clipb, 'compound':'left', 'command':self.__on_read_device_clipboard}},
    {'class':'Button', 'name':'write_clipb', 
         'balloonmsg':'Write the clipboard of an Android device.',
         'config':{'text':'Write', 'image':image_write_clipb, 'compound':'left', 'command':self.__on_write_device_clipboard}} # To Do: Change it. 
]},
    
{'class':'Group', 'pack':{'side':'left', 'fill':'y'}, 'setattr':{'name':'Storage'}, 'children':[
    {'class':'Button', 'name':'get_file',
         'balloonmsg':'Get gallery photos.',
         'config':{'text':'Get Image', 'image':image_get_image, 'command':self.__on_pick_gallery_photo}},
    {'class':'Button', 'name':'get_image',
         'balloonmsg':'Get File',
         'config':{'text':'Get File', 'image':image_get_file, 'command':self.__on_get_device_file}}
]},

{'class':'Group', 'pack':{'side':'left', 'fill':'y'}, 'setattr':{'name':'Sensors'}, 'children':[
    {'class':'Button', 'name':'read_gps',
         'balloonmsg':'Read the AGPS sensor of an Android device.',
         'config':{'text':'Location', 'image':image_sensor_location, 'compound':'left', 'command':self.__on_read_device_location}}
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
        self.__save_file_dir = None
        self.__ip_port = None
        self.__lock = Lock()

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
        
        
        
    def __enable_transfer_widgets(self, enable=True):
        w = self.__widgets
        widgets = [
            w['read_clipb'],
            w['write_clipb'],
            w['get_file'],
            w['get_image'],
            w['read_gps']]
        for widget in widgets:
            widget['state'] = 'normal' if enable else 'disabled'
        
        
        
    @property
    def qr_size(self):
        return int(self.__widgets['qr_size'].entry_text)
        
        
    @property
    def device_data(self):
        return self.__data
        
        
    def _launch_server(self, command):                
        sockobj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
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
            with self.__lock:
                self.__ip_port = (self_ip, self_port)
            self.__password = password = random.randint(0, 65535)
            qr_string = json.dumps({'ip':self_ip, 'port':self_port, 'password':password, 'command':command})
            image = qrcode.make(qr_string).resize((self.qr_size, self.qr_size))        
            self.__qr_image = ImageTk.PhotoImage(image=image) 
     
            if self.__qr_id is None:
                self.__qr_id = self.__qr_canvas.canvas.create_image((0, 0), image=self.__qr_image, anchor='nw')
            else:
                self.__qr_canvas.canvas.itemconfig(self.__qr_id, image=self.__qr_image) 
            self.__data_book.select(self._qr_tab)
        except Exception as err:            
            sockobj.close()
            with self.__lock:
                self.__ip_port = None
            raise err
            
        self.__enable_transfer_widgets(False)
        
        # Launch the data transfer thread    
        @self.root_node.thread_manager.new_thread_do
        def transfer():
            def show_head(device_code, addr, read):
                mark = '=' if read else '*'
                direction = 'From' if read else 'To'
                wtext = self.__scrolled_text
                wtext.append_text(f'''
{mark*30}
{direction} Device
Device Code: {device_code}
IP: {addr[0]}
{datetime.datetime.now().isoformat()}
{mark*30}''')   
                
                
            def generate_plugin_link(data, type_):
                wtext = self.__scrolled_text
                
                for plugin in _plugins[type_]:
                    if not plugin.test_data(data):
                        continue
                    
                    @wtext.create_link_tag
                    def link_action(dumb, plugin=plugin):
                        plugin.action(data)
                    
                    wtext.append_text(f'[{plugin.link_text}]', link_action)
                    wtext.append_text(' ')   
                    
                    
            def recv_head(conn):
                exit_flag = conn.recv(1)
                if exit_flag != b'\x00':
                    # The first byte is not zero, which means abort this transfer mission.
                    return True, None, 0
                password = struct.unpack('!I', conn.recv(4))[0]
                if password != self.__password:
                    return True, None, 0
                device_code = conn.recv(MAXDEVCODELEN).decode('utf-8')
                datalen = struct.unpack('!I', conn.recv(4))[0]
                return False, device_code, datalen
            
            
            def recv_data(conn):
                data_list = []
                while True:
                    data = conn.recv(8192)
                    if not data:
                        break
                    data_list.append(data)
                return b''.join(data_list)
                
            
            try:
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
                # [exit_flag:1byte] [password:4bytes] [data:arbitrary bytes in json format]
                
                conn, addr = sockobj.accept()
                
                @self.root_node.thread_manager.main_thread_do(block=False)
                def clear_qr_image():
                    # Always manipulate the GUI components in the main thread.
                    self.__qr_canvas.canvas.delete(self.__qr_id)
                    self.__qr_id = None
        
                exit_flag, device_code, datalen = recv_head(conn)
                if exit_flag:
                    return
                    
                if command['action'] == 'read':
                    # Loop receiving data
                    if command['source'] != 'storage':
                        # For file transfer mission,
                        # if the file is large, recv_data will be memory consuming. 
                        data = recv_data(conn)
                    # End receiving data            
                    
                    if command['source'] in ('clipboard', 'location_sensor'):
                        # Store received data
                        text = data.decode('utf-8')
                        data_obj = json.loads(text)
                        text = data_obj['data']
                        self.__data = {'data':text, 'type':'text'}
                        # End store received data
                        
                        if command['source'] == 'location_sensor':
                            pos = json.loads(text)                    
                            text = f'latitude={pos["latitude"]}, longitude={pos["longitude"]}'
                        
                        @self.root_node.thread_manager.main_thread_do(block=False)
                        def show_text():
                            # Always manipulate the GUI components in the main thread!
                            scrolled_text = self.__scrolled_text
                            show_head(device_code=device_code, addr=addr, read=True)
                            scrolled_text.append_text(f'\n\n{text}\n\n\n')
                            
                            generate_plugin_link(data=text, type_='text')
                            if command['source'] == 'location_sensor':
                                generate_plugin_link(data=pos, type_='locationsensor')

                            scrolled_text.append_text('\n'*3)
                            scrolled_text.see('end')
                            
                    elif command['source'] == 'gallery':
                        bio = BytesIO(data)
                        img = Image.open(bio)
                        @self.root_node.thread_manager.main_thread_do(block=False)
                        def show_image():
                            scrolled_text = self.__scrolled_text
                            show_head(device_code=device_code, addr=addr, read=True)
                            scrolled_text.append_text('\n'*2)
                            pil_frame = PILImageFrame(scrolled_text, pil_image=img)
                            scrolled_text.text.window_create('end', window=pil_frame)
                            scrolled_text.append_text('\n'*4)
                            scrolled_text.see('end')
                            
                    elif command['source'] == 'storage':
                        namelen = ord(conn.recv(1))
                        filename = Path(conn.recv(namelen).decode('utf-8'))
                        directory = Path(self.__save_file_dir)
                        path = directory/filename
                        if path.exists():
                            stem, ext = filename.stem, filename.suffix
                            for k in range(1, 10000):
                                filename = f'{stem}[{k}]{ext}'
                                path = directory/filename
                                if not path.exists():
                                    break
                        with path.open('wb') as f:
                            while True:
                                buf = conn.recv(32768)
                                if not buf:
                                    break
                                f.write(buf)
                        @self.root_node.thread_manager.main_thread_do(block=False)
                        def show_info():
                            show_head(device_code=device_code, addr=addr, read=True)
                            scrolled_text = self.__scrolled_text
                            scrolled_text.append_text(f'\n\n{str(path)}\n\n')
                            generate_plugin_link(data=str(path), type_='file')
                            scrolled_text.append_text('\n'*3)
                            scrolled_text.see('end')
                            
                            
                    @self.root_node.thread_manager.main_thread_do(block=False)
                    def on_finish():
                        # Always manipulate the GUI components in the main thread.
                        self.__data_book.select(self._data_tab)
                        if self.__on_finish:
                            self.__on_finish(self.device_data['data'])
                            self.__on_finish = None        
                
                elif command['action'] == 'write':                                        
                    if command['target'] == 'clipboard':
                        text = self.root_node.interfaces.os.clipboard.read()
                        data = {'data':text, 'type':'text'}
                    conn.send(json.dumps(data).encode('utf-8'))
                    @self.root_node.thread_manager.main_thread_do(block=False)
                    def on_finish():
                        self.__data_book.select(self._data_tab)
                        scrolled_text = self.__scrolled_text
                        show_head(device_code=device_code, addr=addr, read=False)
                        scrolled_text.append_text('\n'*3)
                        scrolled_text.see('end')
            finally:
                sockobj.close()
                with self.__lock:
                    self.__ip_port = None 
                @self.root_node.thread_manager.main_thread_do(block=False)
                def enable():
                    self.__enable_transfer_widgets()
                    
    
    @Scripting.printable
    def read_device_clipboard(self, on_finish):
        self._launch_server(command={'action':'read', 'source':'clipboard'})
        self.__on_finish = on_finish
        
        
    @Scripting.printable
    def pick_gallery_photo(self, on_finish):
        self._launch_server(command={'action':'read', 'source':'gallery'})
        self.__on_finish = on_finish
        
        
    def get_device_file(self, savein, on_finish):
        self.__save_file_dir = self.root_node.gui.dialogs.ask_directory(savein)
        self._launch_server(command={'action':'read', 'source':'storage'})
        
        
    @Scripting.printable
    def read_device_location(self, on_finish):
        self._launch_server(command={'action':'read', 'source':'location_sensor'})
        self.__on_finish = on_finish
        
        
    def write_device_clipboard(self):
        self._launch_server(command={'action':'write', 'target':'clipboard'})        
        
        
    def __on_read_device_clipboard(self, on_finish=None):
        with code_printer():
            self.read_device_clipboard(on_finish=on_finish)
            
            
    def __on_read_device_location(self, on_finish=None):
        with code_printer():
            self.read_device_location(on_finish=on_finish)
            
            
    def __on_write_device_clipboard(self):
        with code_printer():
            self.write_device_clipboard()
    

    def __on_pick_gallery_photo(self, on_finish=None):
        with code_printer():
            self.pick_gallery_photo(on_finish=on_finish)
            
            
    def __on_get_device_file(self, on_finish=None):
        with code_printer():
            self.get_device_file(savein=self.root_node.lang_center.wavesynscript.constants.ASK_DIRECTORY, on_finish=on_finish)
            