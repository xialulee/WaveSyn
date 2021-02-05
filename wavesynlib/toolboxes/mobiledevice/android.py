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

from base64 import b64encode
from pathlib import Path
from io import BytesIO
from threading import Lock, Event
from tempfile import TemporaryFile

import qrcode
from PIL import ImageTk, Image

import tkinter as tk
import tkinter.ttk as ttk

from Crypto.Cipher import AES
from Crypto.Util import Padding
from Crypto.Random import get_random_bytes

import hy
from wavesynlib.widgets.tk.tkbasewindow import TkToolWindow
from wavesynlib.widgets.tk.desctotk import hywidgets_to_tk
from wavesynlib.widgets.tk.scrolledcanvas import ScrolledCanvas
from wavesynlib.widgets.tk.scrolledlist import ScrolledList
from wavesynlib.widgets.tk.scrolledtext import ScrolledText
from wavesynlib.widgets.tk.pilimageframe import PILImageFrame
from wavesynlib.languagecenter.wavesynscript import Scripting, WaveSynScriptAPI, code_printer
from wavesynlib.languagecenter.utils import get_caller_dir, call_immediately
from wavesynlib.misc.socketutils import AbortException, InterruptHandler
from .widgets import clipb_grp, storage_grp, sensors_grp, manage_grp
from .viewmodel import ViewModel



_plugins = {'locationsensor':[], 'file':[], 'text':[]}
from wavesynlib.toolboxes.mobiledevice import datatransferclient
MAXDEVCODELEN = datatransferclient.MAXDEVCODELEN



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
            mod_path = f'wavesynlib.toolboxes.mobiledevice.plugins.{name}.{mod_name}'
            mod = importlib.import_module(mod_path)
            _plugins[name].append(mod.Plugin(Scripting.root_node))



def _decrypt_text(encrypted, key, iv):
    aes = AES.new(key, AES.MODE_CBC, iv=iv)
    barr = aes.decrypt(encrypted)
    barr = Padding.unpad(barr, block_size=16)
    text = barr.decode("utf-8")
    return text




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
        self.__view_model = ViewModel(self)
        
        
    def on_connect(self):
        self._gui_images = []

        res_dir = get_caller_dir()/'resources'
        image_read_clipb = ImageTk.PhotoImage(file=res_dir/'readclipb.png')
        image_write_clipb = ImageTk.PhotoImage(file=res_dir/'writeclipb.png')
        image_send_clipb_image = ImageTk.PhotoImage(file=res_dir/'sendclipbimage.png')
        image_send_file = ImageTk.PhotoImage(file=res_dir/'sendfile.png')
        image_get_file = ImageTk.PhotoImage(file=res_dir/'getfile.png')
        image_get_image = ImageTk.PhotoImage(file=res_dir/'getimage.png')
        image_sensor_location = ImageTk.PhotoImage(file=res_dir/'locationsensor.png')
        self._gui_images.extend((image_read_clipb, image_write_clipb, image_send_clipb_image, image_send_file, image_get_file, image_get_image, image_sensor_location))
        
        tool_tabs = self._tool_tabs
        
        default_qr_size = 200
        
        balloon = self.root_node.gui.balloon
        tab = tk.Frame(tool_tabs)

        widgets_desc = [clipb_grp, storage_grp, sensors_grp, manage_grp]
        widgets = hywidgets_to_tk(tab, widgets_desc, view_model=self.__view_model, balloon=balloon)
        widgets["send_clipb_image_btn"]["command"] = self.__on_send_clipboard_image_to_device

        widgets["get_file_btn"]["command"] = self.__on_get_device_file
        widgets["get_image_btn"]["command"] = self.__on_pick_gallery_photo
        widgets["send_image_btn"]["command"] = self.__on_send_image_to_device
        widgets["send_file_btn"]["command"] = self.__on_send_file_to_device

        widgets["read_gps_btn"]["command"] = self.__on_read_device_location

        widgets["misson_abort_btn"]["command"] = self.__on_abort
        widgets["qr_size_lent"].checker_function = self.root_node.gui.value_checker.check_int
        
        self.__widgets = widgets
        ip_list = widgets['ip_list']
        ip_list.list.config(height=4, width=15, exportselection=False)
        addrlist = socket.gethostbyname_ex('')[2]
        for ip in addrlist:
            ip_list.append(ip)
        ip_list.selection_set(0)
        
        tool_tabs.add(tab, text='Data')
        
        tk_object = self.tk_object        
        self.__data_book = data_book = ttk.Notebook(tk_object)
        
        self.__qr_canvas = qr_canvas = ScrolledCanvas(data_book) 
        self.__qr_image = None
        self.__qr_id = None
        self.__password = None
        self.__iv = None
        self.__key = None
        self.__data = None
        self.__on_finish = None
        self.__save_file_dir = None
        self.__send_filename = None
        self.__ip_port = None
        self.__lock = Lock()
        self.__abort_event = Event()

        data_book.add(qr_canvas, text='QR Code')
        
        self.__scrolled_text = scrolled_text = ScrolledText(
            data_book, horizontal_scroll=True)
        scrolled_text.disable_keys = True
        scrolled_text.auto_url_link = True
        
        def on_url_link_click(url):
            with code_printer():
                self.root_node.webbrowser_open(url)
                
        scrolled_text.on_url_link_click = on_url_link_click
        
        data_book.add(scrolled_text, text='History')
        
        data_book.pack(expand='yes', fill='both')
        
        self._make_window_manager_tab()        
        
        
    def __enable_transfer_widgets(self, enable=True):
        w = self.__widgets
        widgets = [
            w['get_file_btn'],
            w['get_image_btn'],
            w['read_gps_btn'],
            w['send_clipb_image_btn'],
            w['send_image_btn'],
            w['send_file_btn']]
        for widget in widgets:
            widget['state'] = 'normal' if enable else 'disabled'
        
        
        
    @property
    def qr_size(self):
        return int(self.__widgets['qr_size_lent'].entry_text)
        
        
    @property
    def device_data(self):
        return self.__data
        
        
    def _launch_server(self, command):                
        sockobj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        abort_event = self.__abort_event
        abort_event.clear()
        self_ip = self.__widgets['ip_list'].current_data[0]

        try:
            port = 10000
            while True:
                try:
                    sockobj.bind((self_ip, port))
                except socket.error:
                    port += 1
                    if port > 65535:
                        raise socket.error
                else:
                    break
    
            self_port = port
            with self.__lock:
                self.__ip_port = (self_ip, self_port)

            self.__password = password = random.randint(0, 65535)
            self.__iv = iv = get_random_bytes(16)
            self.__key = key = get_random_bytes(32)

            qr_string = json.dumps({
                "ip":       self_ip, 
                "port":     self_port, 
                "password": password, 
                "aes": {
                    "iv":   b64encode(iv).decode(),
                    "key":  b64encode(key).decode()},
                "command":  command})
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
        self.__view_model.idle.set(False)
        
        # Launch the data transfer thread    
        @self.root_node.thread_manager.new_thread_do
        def transfer():
            def show_head(datainfo, addr, read):
                mark = '=' if read else '*'
                direction = 'From' if read else 'To'
                wtext = self.__scrolled_text
                wtext.append_text(f'''
{mark*60}
{direction} Device
Device Info: 
    Manufacturer: {datainfo["manufacturer"]}
    Model:        {datainfo["model"]}
IP: {addr[0]}
{datetime.datetime.now().isoformat()}
{mark*60}''')   
                
                
            def clear_qr_image():
                self.__qr_canvas.canvas.delete(self.__qr_id)
                self.__qr_id = None                
                
                
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
                    

            def recv_head(ih):
                exit_flag = ih.recv(1)
                if exit_flag != b'\x00':
                    # WaveSyn can abort a misson by sending a zero to itself.
                    return True, None, 0
                head_len = struct.unpack("!I", ih.recv(4))[0]
                head_json = ih.recv(head_len).decode("utf-8")
                head_obj = json.loads(head_json)
                if head_obj["password"] != self.__password:
                    return True, None, 0
                info_len = head_obj["info_len"]
                encrypted_info = ih.recv(info_len)
                decrypted_info = _decrypt_text(encrypted_info, key=self.__key, iv=self.__iv)
                datainfo = json.loads(decrypted_info)
                return False, datainfo, head_obj["data_len"]
            
            
            def recv_data(ih):
                data_list = []
                while True:
                    data = ih.recv(8192)
                    if not data:
                        break
                    data_list.append(data)
                return b''.join(data_list)
                
            
            try:
                sockobj.listen(2)
                sockobj.settimeout(0.5)
                abort_flag = False
                while True:
                    try:
                        conn, addr = sockobj.accept()
                    except socket.timeout:
                        if abort_event.is_set():
                            abort_flag = True
                            break
                    else:
                        break
                    
                if abort_flag:
                    raise AbortException
                    
                ih = InterruptHandler(conn, 0.5, lambda dumb: abort_event.is_set())

                # Always manipulate the GUI components in the main thread.                
                self.root_node.thread_manager.main_thread_do(block=False)(clear_qr_image)
        
                exit_flag, datainfo, datalen = recv_head(ih)
                if exit_flag:
                    return
                    
                if command['action'] == 'read':
                    data = None

                    # Loop receiving data
                    if command['source'] != 'storage':
                        # For file transfer mission,
                        # if the file is large, recv_data will be memory consuming. 
                        data = recv_data(ih)
                    # End receiving data            
                    
                    if command['source'] in ('clipboard', 'location_sensor'):
                        # Store received data
                        text = _decrypt_text(data, key=self.__key, iv=self.__iv)
                        self.__data = {
                            "data": text,
                            "type": "text"}
                        
                        if command['source'] == 'location_sensor':
                            pos = json.loads(text)                    
                            text = f'latitude={pos["latitude"]}, longitude={pos["longitude"]}'
                        
                        @self.root_node.thread_manager.main_thread_do(block=False)
                        def show_text():
                            # Always manipulate the GUI components in the main thread!
                            scrolled_text = self.__scrolled_text
                            show_head(datainfo, addr=addr, read=True)
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
                            show_head(datainfo, addr=addr, read=True)
                            scrolled_text.append_text('\n'*2)
                            pil_frame = PILImageFrame(
                                scrolled_text.text, 
                                pil_image=img, 
                                balloon=self.root_node.gui.balloon)
                            scrolled_text.text.window_create('end', window=pil_frame)
                            scrolled_text.append_text('\n'*4)
                            scrolled_text.see('end')
                            
                    elif command['source'] == 'storage':
                        filename = Path(datainfo["filename"])
                        directory = Path(self.__save_file_dir)
                        path = directory/filename
                        if path.exists():
                            stem, ext = filename.stem, filename.suffix
                            for k in range(1, 10000):
                                filename = f'{stem}[{k}]{ext}'
                                path = directory/filename
                                if not path.exists():
                                    break
                        with TemporaryFile() as tf:
                            recvcnt = 0
                            self.root_node.thread_manager.main_thread_do(block=False)(lambda: self.__view_model.transfer_progress.set(0))
                            while True:
                                buf = ih.recv(65536)
                                if not buf:
                                    self.root_node.thread_manager.main_thread_do(block=False)(lambda: self.__view_model.transfer_progress.set(0))
                                    break
                                tf.write(buf)
                                recvcnt += len(buf)
                                self.root_node.thread_manager.main_thread_do(block=False)(lambda: self.__view_model.transfer_progress.set(int(recvcnt/datalen*100)))
                            
                            tf.seek(0, 0)
                            with path.open('wb') as f:
                                buflen = 65536
                                aes = AES.new(self.__key, AES.MODE_CBC, iv=self.__iv)
                                last_buf = b""
                                while True:
                                    buf = tf.read(buflen)
                                    recvcnt += buflen
                                    decrypted_buf = aes.decrypt(last_buf)
                                    if not buf:
                                        decrypted_buf = Padding.unpad(decrypted_buf, block_size=16)
                                    f.write(decrypted_buf)
                                    if not buf:
                                        break
                                    else:
                                        last_buf = buf

                        @self.root_node.thread_manager.main_thread_do(block=False)
                        def show_info():
                            show_head(datainfo, addr=addr, read=True)
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
                        ih.send(json.dumps(data).encode('utf-8'))
                    elif command['target'].startswith('dir:'):
                        if command['source'] == 'clipboard:image':
                            from PIL import ImageGrab
                            image = ImageGrab.grabclipboard()
                            if not image:
                                raise TypeError('No image in clipboard.')
                            bio = BytesIO()
                            image.save(bio, format='png')
                            ih.send(bio.getvalue())
                            bio.close()
                        elif command['source'].startswith('storage'):
                            filename = Path(self.__send_filename)
                            filelen = filename.stat().st_size
                            sendcnt = 0
                            buflen = 65536
                            with open(filename, 'rb') as file_send:
                                while True:                                    
                                    buf = file_send.read(buflen)
                                    if not buf:
                                        self.__view_model.transfer_progress.set(0)
                                        break
                                    ih.send(buf)
                                    sendcnt += len(buf)
                                    self.__view_model.transfer_progress.set(int(sendcnt/filelen*100))
                    @self.root_node.thread_manager.main_thread_do(block=False)
                    def on_finish():
                        self.__data_book.select(self._data_tab)
                        scrolled_text = self.__scrolled_text
                        show_head(datainfo, addr=addr, read=False)
                        scrolled_text.append_text('\n'*3)
                        scrolled_text.see('end')
            except AbortException:
                self.root_node.thread_manager.main_thread_do(block=False)(clear_qr_image)
            finally:
                sockobj.close()
                with self.__lock:
                    self.__ip_port = None 
                @self.root_node.thread_manager.main_thread_do(block=False)
                def finished():
                    self.__enable_transfer_widgets(True)
                    self.__view_model.idle.set(True)
                    
    
    @WaveSynScriptAPI
    def read_device_clipboard(self, on_finish):
        self._launch_server(command={'action':'read', 'source':'clipboard'})
        self.__on_finish = on_finish
        
        
    @WaveSynScriptAPI
    def pick_gallery_photo(self, on_finish):
        self._launch_server(command={'action':'read', 'source':'gallery'})
        self.__on_finish = on_finish
        
    
    @WaveSynScriptAPI    
    def get_device_file(self, savein, on_finish):
        self.__save_file_dir = self.root_node.gui.dialogs.constant_handler_ASK_DIRECTORY(savein)
        self._launch_server(command={'action':'read', 'source':'storage'})
        
        
    @WaveSynScriptAPI
    def read_device_location(self, on_finish):
        self._launch_server(command={'action':'read', 'source':'location_sensor'})
        self.__on_finish = on_finish
        
    
    @WaveSynScriptAPI    
    def write_device_clipboard(self):
        self._launch_server(command={'action':'write', 'source':'', 'target':'clipboard'}) 
        
    
    @WaveSynScriptAPI    
    def send_clipboard_image_to_device(self):
        self._launch_server(command={
            'action':'write', 
            'target':'dir:Download', 
            'source':'clipboard:image', 
            'name':f'clipboard_{int(datetime.datetime.now().timestamp())}.png'})
    
    
    @WaveSynScriptAPI
    def send_image_to_device(self, filename):
        filename = Path(self.root_node.gui.dialogs.constant_handler_ASK_OPEN_FILENAME(filename))
        self.__send_filename = filename
        self._launch_server(command={
            'action':'write',
            'target':'dir:Download',
            'source':'storage:image',
            'name':f'from_pc_{filename.name}'})
    
    
    @WaveSynScriptAPI
    def send_file_to_device(self, filename):
        filename = Path(self.root_node.gui.dialogs.constant_handler_ASK_OPEN_FILENAME(filename))
        self.__send_filename = filename
        self._launch_server(command={
            'action':'write',
            'target':'dir:Download',
            'source':'storage:file',
            'name':f'from_pc_{filename.name}'})
    
    
    @WaveSynScriptAPI
    def abort(self):
        self.__abort_event.set()
    
    
    def __on_abort(self):
        with code_printer():
            self.abort()
        
        
    def __on_read_device_location(self, on_finish=None):
        with code_printer():
            self.read_device_location(on_finish=on_finish)
            
            
    def __on_send_clipboard_image_to_device(self):
        with code_printer():
            self.send_clipboard_image_to_device()
            
            
    def __on_send_image_to_device(self):
        with code_printer():
            self.send_image_to_device(filename=self.root_node.lang_center.wavesynscript.constants.ASK_OPEN_FILENAME)
            
            
    def __on_send_file_to_device(self):
        with code_printer():
            self.send_file_to_device(filename=self.root_node.lang_center.wavesynscript.constants.ASK_OPEN_FILENAME)
    

    def __on_pick_gallery_photo(self, on_finish=None):
        with code_printer():
            self.pick_gallery_photo(on_finish=on_finish)
            
            
    def __on_get_device_file(self, on_finish=None):
        with code_printer():
            self.get_device_file(savein=self.root_node.lang_center.wavesynscript.constants.ASK_DIRECTORY, on_finish=on_finish)
            