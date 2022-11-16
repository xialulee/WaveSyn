# -*- coding: utf-8 -*-
"""
Created on Sat Nov 24 00:34:39 2018

@author: Feng-cong Li
"""

from __future__ import annotations

import ctypes
from copy import deepcopy
from ctypes import byref
from ctypes.wintypes import MSG, UINT
from queue import Empty, Queue
from typing import Final, Callable, Iterable, Mapping
from dataclasses import dataclass

from win32con import PM_REMOVE, WM_HOTKEY

from wavesynlib.languagecenter.designpatterns import Observable
from wavesynlib.languagecenter.wavesynscript import ModelNode

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
    for bitpos, name in _attr_names:
        def __getter(self, bitpos=bitpos) -> int:
            return self.value & (1 << bitpos)
        
        def __setter(self, val: bool, bitpos=bitpos) -> None:
            if val:
                self.value |= 1 << bitpos
            else:
                self.value &= ~(1 << bitpos)
                
        locals()[name] = property(__getter).setter(__setter)



@dataclass
class HotkeyInfo:
    modifiers: Modifiers 
    vk:        int
    func:      Callable[[], None]
                



def _modifier_name_convert(name: str) -> str:
    name = name.lower()
    if name in ["alt", "menu"]:
        return "alt"   
    if name in ["ctrl", "control"]:
        return "ctrl"
    if name == "shift":
        return "shift" 



def _modifier_names_to_obj(modifiers: Iterable[str]) -> Modifiers:
    modobj = Modifiers(0)
    for modifier in modifiers:
        setattr(modobj, _modifier_name_convert(modifier), 1)
    return modobj



class GlobalHotkeyManager(ModelNode, Observable):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__hotkey_info: Mapping[int, HotkeyInfo] = {}
        self.__repeater = None
        self.__queue = Queue()
        self.__timer = None

        @self.add_observer
        def on_event(id_: int, info: HotkeyInfo) -> None:
            if func := info.func:
                func()
                
    def on_connect(self) -> None:
        self.__timer = timer = self.root_node.create_timer(interval=50)
        @timer.add_observer
        def on_timer(event=None):
            try:
                while True:
                    id_ = self.__queue.get_nowait()
                    self.notify_observers(id_, self.__hotkey_info[id_])
            except Empty:
                pass

    def set_timer_interval(self, interval: int) -> None:
        self.__timer.interval = interval

    def start_timer(self) -> None:
        self.__timer.active = True

    def stop_timer(self) -> None:
        self.__timer.active = False

    def __get_new_id(self) -> int:
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
    def hotkey_info(self) -> Mapping[int, HotkeyInfo]:
        return deepcopy(self.__hotkey_info)

    def register(self, 
            modifiers: Iterable[str], 
            vk:        int, 
            func:      Callable[[], None] = None
        ) -> int:
        modifiers = _modifier_names_to_obj(modifiers)
        id_ = self.__get_new_id()
        success = self._repeater.do_once(lambda: 
            _user32.RegisterHotKey(None, id_, modifiers, vk))
        if success:
            self.__hotkey_info[id_] = HotkeyInfo(modifiers, vk, func)
        return success

    def unregister(self, 
            modifiers: Iterable[str] = None, 
            vk:        int = None, 
            id_:       int = None
        ) -> None:
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

    def unregister_all(self) -> None:
        for id_ in tuple(self.__hotkey_info.keys()):
            self.unregister(id_=id_)
