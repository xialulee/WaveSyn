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
            constants = self.root_node.interfaces.os.windows.window_handle_getter.constants
            handle = constants.constant_handler_HWND_ARBITRARY(handle)
            handle = constants.constant_handler_HWND_FOREGROUND(handle)
            handle = constants.constant_handler_HWND_WINDOW_FROM_CURSOR_POS(handle)
            self._send_command(handle, command)
        return method
        
    for name in command_names:
        if name.startswith('APPCOMMAND_'):
            method_name = name[len('APPCOMMAND_'):].lower()
            command_value = getattr(constants, name)
            method = _method_generator(command_value)
            locals()[method_name] = method
                