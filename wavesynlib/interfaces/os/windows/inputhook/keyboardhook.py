import ctypes as ct


SetWindowsHookExA   = ct.windll.user32.SetWindowsHookExA
UnhookWindowsHookEx = ct.windll.user32.UnhookWindowsHookEx
CallNextHookEx      = ct.windll.user32.CallNextHookEx

import win32con

from win32con import (
    WM_KEYDOWN,
    WM_KEYUP,
    WH_KEYBOARD_LL)


import atexit


from wavesynlib.languagecenter.wavesynscript import ModelNode
from wavesynlib.languagecenter.datatypes.wintypes.hook import KHOOKPROC
from wavesynlib.interfaces.os.windows.inputsender.utils import send_mouse_input



class _KeyToMouse:
    def __init__(self, mouse_btn):
        self.__previous = None
        self.__mouse_btn = mouse_btn


    def __callback(self, key_stat) -> bool:
        if self.__previous == key_stat:
            return True
        else:
            self.__previous = key_stat
            kwargs = {
                "dx": 0,
                "dy": 0, 
                "button": self.__mouse_btn }
            if key_stat == "keydown":
                kwargs["press"] = True
            elif key_stat == "keyup":
                kwargs["release"] = True
            else:
                raise ValueError("key_stat not supported. ")
            send_mouse_input(**kwargs)
            return True


    def on_keydown(self) -> bool:
        return self.__callback("keydown")


    def on_keyup(self) -> bool:
        return self.__callback("keyup")



class KeyboardHook(ModelNode):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__remap = {}
        self.__hkhook = None
        self.__c_khook = KHOOKPROC(self.__khookproc)


    def add_key_to_mouse(self, key, mouse_btn):
        mapobj = _KeyToMouse(mouse_btn=mouse_btn)
        self.__remap[key] = mapobj


    def __khookproc(self, nCode, wParam, lParam):
        vk_code = lParam.contents.vkCode
        mapobj = self.__remap.get(vk_code, None)
        if mapobj:
            if wParam == WM_KEYDOWN:
                eat = mapobj.on_keydown()
            elif wParam == WM_KEYUP:
                eat = mapobj.on_keyup()
            else:
                eat = False
            if eat:
                return -1
        return CallNextHookEx(self.__hkhook, nCode, wParam, lParam)


    def hook(self):
        self.__hkhook = SetWindowsHookExA(WH_KEYBOARD_LL, self.__c_khook, None, 0)
        if not self.__hkhook:
            raise OSError("Failed to setup global keyboard hook.")


    def unhook(self):
        UnhookWindowsHookEx(self.__hkhook)


    def unhook_at_exit(self):
        atexit.register(self.unhook)
