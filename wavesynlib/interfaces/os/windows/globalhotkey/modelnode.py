# -*- coding: utf-8 -*-
"""
Created on Sat Nov 24 00:34:39 2018

@author: Feng-cong Li
"""
import os
from pathlib import Path
import hy
try:
    from wavesynlib.interfaces.os.windows.globalhotkey.hynode \
        import GlobalHotkeyManager
except hy.errors.HyCompileError:
    node_path = Path(__file__).parent / 'hynode.hy'
    os.system(f'hyc {node_path}')
    from wavesynlib.interfaces.os.windows.globalhotkey.hynode \
        import GlobalHotkeyManager    
    

#import ctypes
#from ctypes import byref
#from ctypes.wintypes import MSG
#import win32con
#_user32 = ctypes.windll.user32
#from copy import deepcopy
#
#from wavesynlib.languagecenter.wavesynscript import ModelNode
#
#_ID_UPPER_BOUND = 0xBFFF + 1
#
#
#
#class GlobalHotkeyManager(ModelNode):
#    def __init__(self, *args, **kwargs):
#        super().__init__(*args, **kwargs)
#        self.__hotkey_info = {}
#        self.__repeater = None
#        
#        
#    def __get_new_id(self):
#        for i in range(1, _ID_UPPER_BOUND):
#            if i not in self.__hotkey_info:
#                return i
#         
#        
##    def __repeat_func(self):
##        msg = MSG()            
##        # Handle hotkey messages.
##        if _user32.PeekMessageW(byref(msg), -1, 0, 0, win32con.PM_REMOVE):
##            if msg.message == win32con.WM_HOTKEY:
##                info = self.__hotkey_info.get(msg.wParam, lambda:None)
##                info[-1]()
#                
#                
#    @property
#    def _repeater(self):
#        if not self.__repeater:
#            def thread_func():
#                msg = MSG()
#                if _user32.PeekMessageW(byref(msg), -1, 0, 0, win32con.PM_REMOVE):
#                    if msg.message == win32con.WM_HOTKEY:
#                        info = self.__hotkey_info.get(msg.wParam, lambda:None)
#                        info[-1]()
#            self.__repeater = self.root_node.thread_manager.create_repeater_thread(thread_func)
#            self.__repeater.daemon = True
#            self.__repeater.start()
#        return self.__repeater
#                
#        
#    @property
#    def hotkey_info(self):
#        return deepcopy(self.__hotkey_info)
#        
#        
#    def register(self, modifiers, vk, func, call_in_main_thread=True):
##        if not self.__repeater:
##            self.__repeater = \
##                self.root_node.thread_manager.create_repeater_thread(
##                    self.__repeat_func)
##            self.__repeater.daemon = True
##            self.__repeater.start()
#        
#        if call_in_main_thread:
#            def f():
#                self.root_node.thread_manager.main_thread_do(block=True)(func)
#        else:
#            f = func
#            
#        id_ = self.__get_new_id()
#        
#        def register_in_repeater():
#            return _user32.RegisterHotKey(None, id_, modifiers, vk)
#        
#        success = self._repeater.do_once(register_in_repeater)
#        if success:
#            self.__hotkey_info[id_] = (modifiers, vk, f)            
#               
#        return success
#    
#    
#    def unregister(self, modifiers=None, vk=None, id_=None):
#        if not id_:
#            for key, val in self.__hotkey_info.items():
#                if val[0] == modifiers and val[1] == vk:
#                    id_ = key
#                    break
#        if id_:
#            def unregister_in_repeater():
#                _user32.UnregisterHotKey(None, id_)
#            self._repeater.do_once(unregister_in_repeater)
#            del self.__hotkey_info[id_]          
#
#                
#    def unregister_all(self):
#        for id_ in tuple(self.__hotkey_info.keys()):
#            self.unregister(id_=id_)