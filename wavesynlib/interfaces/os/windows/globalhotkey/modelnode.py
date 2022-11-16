# -*- coding: utf-8 -*-
"""
Created on Sat Nov 24 00:34:39 2018

@author: Feng-cong Li
"""

from __future__ import annotations
from typing import Final

import ctypes
from ctypes import byref
from ctypes.wintypes import UINT, MSG
from copy import deepcopy
from queue import Queue, Empty

from win32con import WM_HOTKEY, PM_REMOVE

from wavesynlib.languagecenter.wavesynscript import ModelNode
from wavesynlib.languagecenter.designpatterns import Observable

_user32 = ctypes.windll.user32
_ID_UPPER_BOUND: Final[int] = 0xBFFF + 1


class Modifiers(UINT):
    _attr_names = [
        [0,  "alt"], 
        [1,  "ctrl"], 
        [2,  "shift"], 
        [3,  "win"], 
        [14, "norepeat"]
    ]
    for [bitpos, name] in _attr_names:
        def __getter(self, bitpos=bitpos) -> int:
            return self.value & (1 << bitpos)
        
        def __setter(self, val: bool, bitpos=bitpos) -> None:
            if val:
                self.value |= 1 << bitpos
            else:
                self.value &= ~(1 << bitpos)
                
        locals()[name] = property(__getter).setter(__setter)
                



def _modifier_name_convert(name):
    name = name.lower()
    if name in ["alt", "menu"]:
        return "alt"   
    if name in ["ctrl", "control"]:
        return "ctrl"
    if name == "shift":
        return "shift" 



def _modifier_names_to_obj(modifiers):
    modobj = Modifiers(0)
    for modifier in modifiers:
        setattr(modobj, _modifier_name_convert(modifier), 1)
    return modobj



class GlobalHotkeyManager(ModelNode, Observable):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__hotkey_info = {}
        self.__repeater = None
        self.__queue = Queue()
        self.__timer = None

        @self.add_observer
        def on_event(id_, info):
            it = info[2]
            if it:
                it()
                
    def on_connect(self):
        self.__timer = timer = self.root_node.create_timer(interval=50)
        @timer.add_observer
        def on_timer(event=None):
            try:
                while True:
                    id_ = self.__queue.get_nowait()
                    self.notify_observers(id_, self.__hotkey_info[id_])
            except Empty:
                pass

    def set_timer_interval(self, interval):
        self.__timer.interval = interval

    def start_timer(self):
        self.__timer.active = True

    def stop_timer(self):
        self.__timer.active = False

    def __get_new_id(self):
        for i in range(1, _ID_UPPER_BOUND):
            if i not in self.__hotkey_info:
                return i

    @property
    def _repeater(self):
        if not self.__repeater:
            @self.root_node.thread_manager.create_repeater_thread
            def repeater_thread():
                msg = MSG()
                if _user32.PeekMessageW(byref(msg), None, 0, 0, PM_REMOVE) \
                        and msg.message == WM_HOTKEY:
                    id_ = msg.wParam
                    self.__queue.put(id_)
            self.__repeater = repeater_thread
            repeater_thread.daemon = True
            repeater_thread.start()
            self.start_timer()
        return self.__repeater
    
    @property
    def hotkey_info(self):
        return deepcopy(self.__hotkey_info)

    def register(self, modifiers, vk, func=None):
        modifiers = _modifier_names_to_obj(modifiers)
        id_ = self.__get_new_id()
        success = self._repeater.do_once(lambda : 
            _user32.RegisterHotKey(None, id_, modifiers, vk))
        if success:
            self.__hotkey_info[id_] = modifiers, vk, func
        return success

    def unregister(self, modifiers=None, vk=None, id_=None):
        if modifiers:
            modifiers = _modifier_names_to_obj(modifiers)
        if not id_:
            for key, val in self.__hotkey_info.items():
                if val[0] == modifiers and val[1] == vk:
                    id_ = key
                    break
        if id_:
            self._repeater.do_once(lambda: 
                _user32.UnregisterHotKey(None, id_))
            del self.__hotkey_info[id_]

    def unregister_all(self):
        for id_ in tuple(self.__hotkey_info.keys()):
            self.unregister(id_=id_)
