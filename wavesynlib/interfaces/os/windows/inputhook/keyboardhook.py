import hy
from ctypes import windll
from win32con import WM_KEYDOWN, WM_KEYUP, WH_KEYBOARD_LL
import atexit
from abc import ABC
from typing import Final

from wavesynlib.languagecenter.wavesynscript import ModelNode
from wavesynlib.languagecenter.datatypes.wintypes.hook import KHOOKPROC
from wavesynlib.interfaces.os.windows.inputsender.utils import send_mouse_input, send_key_input

SetWindowsHookExA: Final   = windll.user32.SetWindowsHookExA
UnhookWindowsHookEx: Final = windll.user32.UnhookWindowsHookEx
CallNextHookEx: Final      = windll.user32.CallNextHookEx


class KeyToAction(ABC):
    def on_keydown(self) ->bool:
        raise NotImplementedError()

    def on_keyup(self) ->bool:
        raise NotImplementedError()


class KeyToMouse(KeyToAction):
    def __init__(self, mouse_btn: str) -> None:
        self.__previous = None
        self.__mouse_btn = mouse_btn

    def __callback(self, key_stat: str) -> bool:
        if self.__previous == key_stat:
            return True
        else:
            self.__previous = key_stat
            if key_stat == 'keydown':
                press_or_release = {'press': True}
            elif key_stat == "keyup":
                press_or_release = {'release': True}
            else:
                raise ValueError('key_stat not supported.')
            send_mouse_input(**{
                'dx': 0, 
                'dy': 0, 
                'button': self.__mouse_btn, 
                **press_or_release
            })
            return True

    def on_keydown(self) -> bool:
        return self.__callback('keydown')

    def on_keyup(self) -> bool:
        return self.__callback('keyup')


class KeyToKey(KeyToAction):
    def __init__(self, new_key_code: int, modifiers=[]) -> None:
        self.__new_key_code = new_key_code
        self.__modifiers = modifiers

    def on_keydown(self) -> bool:
        for m in self.__modifiers:
            send_key_input(m, press=True)
        send_key_input(self.__new_key_code, press=True)
        return True

    def on_keyup(self) -> bool:
        for m in self.__modifiers:
            send_key_input(m, release=True)
        send_key_input(self.__new_key_code, release=True)
        return True


class KeyboardHook(ModelNode):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__remap = {}
        self.__hkhook = None
        self.__c_khook = KHOOKPROC(self.__khookproc)

    def add_key_to_mouse(self, key: int, mouse_btn: str) -> None:
        mapobj = KeyToMouse(mouse_btn=mouse_btn)
        self.__remap[key] = mapobj

    def add_key_to_key(self, old_key: int, new_key: int) -> None:
        mapobj = KeyToKey(new_key_code=new_key)
        self.__remap[old_key] = mapobj

    def add_key_to_action(self, key: int, action: KeyToAction) -> None:
        self.__remap[key] = action

    def __khookproc(self, nCode, wParam, lParam):
        vk_code = lParam.contents.vkCode
        mapobj = self.__remap.get(vk_code, None)
        if mapobj:
            eat = {
                WM_KEYDOWN: mapobj.on_keydown, 
                WM_KEYUP: mapobj.on_keyup
            }.get(wParam, lambda : False)
            if eat():
                return -1
        return CallNextHookEx(self.__hkhook, nCode, wParam, lParam)

    def hook(self):
        self.__hkhook = SetWindowsHookExA(
            WH_KEYBOARD_LL, self.__c_khook, None, 0)
        if not self.__hkhook:
            raise OSError('Failed to setup global keyboard hook.')

    def unhook(self):
        return UnhookWindowsHookEx(self.__hkhook)

    def unhook_at_exit(self):
        return atexit.register(self.unhook)
