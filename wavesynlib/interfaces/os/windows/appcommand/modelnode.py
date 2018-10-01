# -*- coding: utf-8 -*-
"""
Created on Mon Oct  1 16:43:01 2018

@author: Feng-cong Li
"""

from ctypes import windll

from wavesynlib.languagecenter.wavesynscript import ModelNode
from wavesynlib.interfaces.os.windows.appcommand import constants



class AppCommand(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
    def _send_command(self, handle, command):
        windll.user32.PostMessageA(handle, constants.WM_APPCOMMAND, handle, command<<16)
        
        
    command_names = dir(constants)
    
    def _method_generator(command):
        def method(self, handle):
            constants = self.root_node.interfaces.os.windows.wsscriptconstants
            handle = constants.hwnd_arbitrary(handle)
            handle = constants.hwnd_foreground(handle)
            handle = constants.hwnd_from_cursor_pos(handle)
            self._send_command(handle, command)
        return method
        
    for name in command_names:
        if name.startswith('APPCOMMAND_'):
            method_name = name[len('APPCOMMAND_'):].lower()
            command_value = getattr(constants, name)
            method = _method_generator(command_value)
            locals()[method_name] = method
                