# -*- coding: utf-8 -*-
"""
Created on Thu Mar 02 22:41:20 2017

@author: Feng-cong Li
"""

from subprocess import Popen
import webbrowser
import comtypes
from comtypes import client

from wavesynlib.languagecenter.utils import get_caller_dir
from wavesynlib.languagecenter.wavesynscript import Scripting, ModelNode
from wavesynlib.interfaces.os.windows.wmi import WQL


app_paths = {
    'cmd': 'cmd',
    'powershell': 'powershell'
}



class WMI(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__wql = None
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
        
       
    @Scripting.printable
    def query(self, wql, output_format='original'):
        '''Launch a WQL query and return the result.
    wql: WQL string.
    output_format: the format of the result.
        "original": return the raw comtypes pointer (default).
        "comtypes": equivalent to "original".
        "native": result converted to Python builtin data types.
        "python": equivalent to "comtypes".
        "json": result converted to JSON string.
        
    Return Value: the result of the query, of which the data type depends on 
        the value of output_format.'''
        wql = self.root_node.gui.dialogs.ask_string(
            wql,
            title='WQL',
            prompt='Please input the WQL string.')
        self.__init_services()
        return self.__wql.query(wql, output_format)
    
        
    @Scripting.printable
    def set_sink(self, sink, wql):
        self.__init_services()
        self.__wql.set_sink(sink, wql)
    


class Windows(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wmi = WMI()
        self.battery = ModelNode(
            is_lazy=True, 
            module_name='wavesynlib.interfaces.os.windows.battery',
            class_name='Battery')
        self.powershell = ModelNode(
            is_lazy=True,
            module_name='wavesynlib.interfaces.os.windows.powershell',
            class_name='Powershell')
        
    
    @Scripting.printable
    def launch(self, app_name, *args):
        if app_name in app_paths:
            app_path = app_paths[app_name]
        else:
            app_path = str(get_caller_dir() / 'apps' / app_name)
        
        if args:
            cmd = ['python', app_path]
            args = [str(arg) for arg in args]
            cmd.extend(args)
            Popen(cmd)
        else:
            webbrowser.open(app_path)
            
            
    @Scripting.printable
    def create_guid(self):
        return str(comtypes.GUID.create_new())
        
        