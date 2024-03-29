# -*- coding: utf-8 -*-
"""
Created on Thu Mar 02 22:41:20 2017

@author: Feng-cong Li
"""

import os
import sys
import comtypes
from comtypes import client
from pathlib import Path
import subprocess as sp
import PIL
import pylab
from io import BytesIO

from wavesynlib.languagecenter.wavesynscript import Scripting, ModelNode, WaveSynScriptAPI
from wavesynlib.interfaces.os.windows.wmi import WQL
from wavesynlib.interfaces.os.windows.shell.windowhandlegetter.modelnode import WindowHandleGetter
from wavesynlib.gadgets.wswhich import which



app_paths = {
    'cmd': 'cmd',
    'powershell': 'powershell'
}



class UoW(ModelNode):
    '''Windows 10 supports the so-called Ubuntu on Windows (UoW), and this node
provides interfaces for calling useful tools on UoW.'''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
    def call_tesseract(self, image, lang=None, on_finish='print'):
        def save_image_to_stream(image, save_func):
            bio = BytesIO()
            save_func(bio, image)
            bio.seek(0)
            return bio
        
        if isinstance(image, PIL.ImageFile.ImageFile):
            image = save_image_to_stream(
                    image, 
                    lambda bio, image: image.save(bio, 'png'))
        elif isinstance(image, pylab.ndarray):
            image = save_image_to_stream(
                    image, 
                    lambda bio, image: pylab.imsave(bio, image, format='png'))
        elif isinstance(image, (str, Path)):
            with open(image, 'rb') as f:
                data = f.read()
            image = save_image_to_stream(
                    data, 
                    lambda bio, data: bio.write(data))
        if on_finish == 'print':
            def print_(retval):
                if retval[0]:
                    print(retval[0].decode('utf-8'))
                if retval[1]:
                    print(retval[1].decode('utf-8'), sys.stderr)
            on_finish = print_
        
        command = ['bash', '-c', 'tesseract stdin stdout']
        if lang:
            command[-1] = f'{command[-1]} -l {lang}'
        p = sp.Popen(command, 
                     stdin=sp.PIPE, 
                     stdout=sp.PIPE)
        image_data = image.read()
        @self.root_node.thread_manager.new_thread_do
        def call():
            retval = p.communicate(input=image_data)
            @self.root_node.thread_manager.main_thread_do(block=False)
            def finish():
                on_finish(retval)
                
                
    @WaveSynScriptAPI
    def convert_to_uow_path(self, path:(Path, str))->str:
        '''Windows 10 supports Ubuntu subsystem named UoW. This subsystem can access
Windows file system. For example:
"C:\\lab" is "/mnt/c/lab" on UoW.

path: a path on Windows.
return value: the corresponding UoW path.'''
        path = Path(path)
        parts = path.parts
        drive = parts[0][:parts[0].find(':')]
        return (Path('/mnt') / drive).joinpath(*parts[1:]).as_posix()                



class WMI(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__wql: WQL|None = None
        self.__services = None
        
        
    def __init_services(self):
        if self.__services is None:
            loc = client.CreateObject('WbemScripting.SWbemLocator')
            self.__services = loc.ConnectServer('.')
            self.__wql = WQL(self.__services)
        
        
    @property
    def services(self):
        self.__init_services()
        return self.__services
        

    @WaveSynScriptAPI
    def query(self, wql, output_format='original'):
        '''\
Launch a WQL query and return the result.
wql: WQL string.
output_format: the format of the result.
    "original": return the raw comtypes pointer (default).
    "comtypes": equivalent to "original".
    "native": result converted to Python builtin data types.
    "python": equivalent to "comtypes".
    "json": result converted to JSON string.
    
Return Value: the result of the query, of which the data type depends on 
    the value of output_format.'''
        wql = self.root_node.gui.dialogs.constant_handler_ASK_STRING(
            wql,
            title='WQL',
            prompt='Please input the WQL string.')
        self.__init_services()
        if self.__wql:
            return self.__wql.query(wql, output_format)
        else:
            raise AttributeError("WMI not initialized.")
    

    @WaveSynScriptAPI
    def gpt_query(self, prompt, output_format='original'):
        '''\
Launch a WQL query and return the result.
wql: WQL string.
output_format: the format of the result.
    "original": return the raw comtypes pointer (default).
    "comtypes": equivalent to "original".
    "native": result converted to Python builtin data types.
    "python": equivalent to "comtypes".
    "json": result converted to JSON string.
    
Return Value: the result of the query, of which the data type depends on 
    the value of output_format.'''
#        wql = self.root_node.gui.dialogs.constant_handler_ASK_STRING(
#            wql,
#            title='WQL',
#            prompt='Please input the WQL string.')
        self.__init_services()
        if self.__wql:
            return self.__wql.gpt_query(prompt, output_format)
        else:
            raise AttributeError("WMI not initialized.")

        
    @WaveSynScriptAPI
    def set_sink(self, sink, wql):
        self.__init_services()
        if self.__wql:
            self.__wql.set_sink(sink, wql)
        else:
            raise AttributeError("WMI not initialized.")
    


class Windows(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wmi = WMI()
        self.uow = UoW()
        self.window_handle_getter = WindowHandleGetter()
        
        self.processes = ModelNode(
            is_lazy=True,
            module_name='wavesynlib.interfaces.os.windows.processes.modelnode',
            class_name='Processes')
        
        self.battery = ModelNode(
            is_lazy=True, 
            module_name='wavesynlib.interfaces.os.windows.battery',
            class_name='Battery')
        
        self.commands = ModelNode(
            is_lazy=True,
            module_name='wavesynlib.interfaces.os.windows.commands',
            class_name='Commands')
        
        self.powershell = ModelNode(
            is_lazy=True,
            module_name='wavesynlib.interfaces.os.windows.powershell',
            class_name='Powershell')
        
        self.appcommand = ModelNode(
            is_lazy=True,
            module_name='wavesynlib.interfaces.os.windows.appcommand.modelnode',
            class_name='AppCommand')
        
        self.global_hotkey_manager = ModelNode(
            is_lazy=True,
            module_name='wavesynlib.interfaces.os.windows.globalhotkey.modelnode',
            class_name='GlobalHotkeyManager')
        
        self.input_senders = ModelNode(
            is_lazy=True,
            module_name='wavesynlib.interfaces.os.windows.inputsender.modelnode',
            class_name='InputSenders')
                
        self.xinput = ModelNode(
            is_lazy=True,
            module_name='wavesynlib.interfaces.os.windows.xinput.modelnode',
            class_name='XInput')

            
    @WaveSynScriptAPI
    def create_guid(self)->str:
        return str(comtypes.GUID.create_new())


    @WaveSynScriptAPI
    def edit_hosts(self, editor=None):
        if not editor:
            editor = "gvim"
        editor_paths = which(editor)
        if editor_paths:
            editor_path = str(editor_paths[0])
        else:
            # The specified editor not installed. Use notepad.exe instead.
            editor_path = str(which("notepad")[0])
        hosts_path = str(self.get_hosts_path())
        self.root_node.interfaces.os.windows.processes.utils.run_as_admin(editor_path, hosts_path)


    @WaveSynScriptAPI
    def get_hosts_path(self):
        root = Path(os.environ["SYSTEMROOT"])
        return root / r"System32\drivers\etc\hosts"
        
        