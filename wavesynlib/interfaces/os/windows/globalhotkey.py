# -*- coding: utf-8 -*-
"""
Created on Sat Nov 24 00:34:39 2018

@author: Feng-cong Li
"""

import ctypes
from ctypes import byref
from ctypes.wintypes import MSG
import win32con
_user32 = ctypes.windll.user32
from copy import deepcopy
from queue import Queue, Empty
import threading

from wavesynlib.languagecenter.wavesynscript import ModelNode

_ID_UPPER_BOUND = 0xBFFF + 1



class GlobalHotkeyManager(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__hotkey_info = {}
        self.__register_success = 0
        self.__command_queue = Queue()
        self.__thread_obj = None
        self.__register_event = threading.Event()
        
        
    def __get_new_id(self):
        for i in range(1, _ID_UPPER_BOUND):
            if i not in self.__hotkey_info:
                return i
            
            
    def __register_in_thread(self, id_, modifiers, vk, func):
        try:
            success = _user32.RegisterHotKey(None, id_, modifiers, vk)
            self.__register_success = success
        finally:
            self.__register_event.set()
            
            
    def __unregister_in_thread(self, id_):
        _user32.UnregisterHotKey(None, id_)
         
        
    def __thread_func(self):
        queue = self.__command_queue
        msg = MSG()
        while True:
            # Handle command from the main thread.
            try:
                while True:
                    command = queue.get_nowait()
                    command[0](*command[1:])
            except Empty:
                pass
            
            # Handle hotkey messages.
            if _user32.PeekMessageW(byref(msg), -1, 0, 0, win32con.PM_REMOVE):
                if msg.message == win32con.WM_HOTKEY:
                    info = self.__hotkey_info.get(msg.wParam, lambda:None)
                    info[-1]()
        
    @property
    def hotkey_info(self):
        return deepcopy(self.__hotkey_info)
        
        
    def register(self, modifiers, vk, func, call_in_main_thread=True):
        self.__register_success = 0
        if not self.__thread_obj:
            self.__thread_obj = \
                self.root_node.thread_manager.create_thread_object(
                    self.__thread_func) 
            self.__thread_obj.daemon = True
            self.__thread_obj.start()
        
        if call_in_main_thread:
            def f():
                print('f')
                self.root_node.thread_manager.main_thread_do(block=True)(func)
        else:
            f = func
            
        id_ = self.__get_new_id()
        self.__command_queue.put((
            self.__register_in_thread, 
            id_, 
            modifiers, 
            vk, 
            f))
        
        self.__register_event.wait()
        self.__register_event.clear()
        if self.__register_success:
            self.__hotkey_info[id_] = (modifiers, vk, func)            
        return self.__register_success
    
    
    def unregister(self, modifiers=None, vk=None, id_=None):
        if not id_:
            for key, val in self.__hotkey_info.items():
                if val[0] == modifiers and val[1] == vk:
                    id_ = key
                    break
        if id_:
            self.__command_queue.put((self.__unregister_in_thread, id_))
            del self.__hotkey_info[id_]          

                
    def unregister_all(self):
        for id_ in self.__hotkey_info.keys():
            self.unregister(id_=id_)