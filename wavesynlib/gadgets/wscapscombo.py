import sys
from dataclasses import dataclass
from tkinter import Tk
import tkinter.messagebox as msgbox
import win32con

from wavesynlib.interfaces.os.windows.inputhook.keyboardhook import KeyboardHook, KeyToAction, KeyToKey, KeyToMouse


@dataclass
class Status:
    # -1 for keydown; 0 for nothing; 1 for keyup
    caps: int = 0


class CapsAction(KeyToAction):
    def __init__(self, status: Status):
        self.__status = status

    def on_keydown(self) -> bool:
        self.__status.caps = -1
        return True

    def on_keyup(self) -> bool:
        self.__status.caps = 1
        return True


class KeyToKeyWithStatus(KeyToKey):
    def __init__(self, new_key_code: int, status:Status, modifiers=[]):
        self.__status = status
        super().__init__(new_key_code, modifiers=modifiers)

    def on_keydown(self) -> bool:
        if self.__status.caps == -1:
            return super().on_keydown()
        else:
            return False

    def on_keyup(self) -> bool:
        if self.__status.caps == -1:
            return super().on_keyup()
        else:
            return False


class KeyToMouseWithStatus(KeyToMouse):
    def __init__(self, mouse_btn: str, status:Status):
        self.__status = status
        super().__init__(mouse_btn)

    def on_keydown(self) -> bool:
        if self.__status.caps == -1:
            return super().on_keydown()
        else:
            return False

    def on_keyup(self) -> bool:
        if self.__status.caps == -1:
            return super().on_keyup()
        else:
            return False


default_map = {
    ord("A"): win32con.VK_LEFT,
    ord("S"): win32con.VK_DOWN,
    ord("D"): win32con.VK_RIGHT,
    ord("W"): win32con.VK_UP,
    ord("Q"): (win32con.VK_LEFT, (win32con.VK_CONTROL,)),
    ord("E"): (win32con.VK_RIGHT, (win32con.VK_CONTROL,)),
    ord("R"): win32con.VK_HOME,
    ord("F"): win32con.VK_END,
    ord("Z"): "left",
    ord("X"): "right",
    ord("C"): "middle",
    ord("M"): win32con.VK_NUMPAD0,
    ord("J"): win32con.VK_NUMPAD1,
    ord("K"): win32con.VK_NUMPAD2,
    ord("L"): win32con.VK_NUMPAD3,
    ord("U"): win32con.VK_NUMPAD4,
    ord("I"): win32con.VK_NUMPAD5,
    ord("O"): win32con.VK_NUMPAD6,
    ord("7"): win32con.VK_NUMPAD7,
    ord("8"): win32con.VK_NUMPAD8,
    ord("9"): win32con.VK_NUMPAD9 }



if __name__ == "__main__":
    khook = KeyboardHook()
    khook.unhook_at_exit()
    status = Status()
    caps_action = CapsAction(status=status)
    khook.add_key_to_action(win32con.VK_CAPITAL, caps_action)
    for k, v in default_map.items():
        if isinstance(v, tuple):
            khook.add_key_to_action(k, KeyToKeyWithStatus(v[0], status, modifiers=v[1]))
        elif isinstance(v, str):
            khook.add_key_to_action(k, KeyToMouseWithStatus(v, status))
        else:
            khook.add_key_to_action(k, KeyToKeyWithStatus(v, status))
    try:
        khook.hook()
    except OSError:
        msgbox.showerror("Error", "Failed to setup a global keyboard hook.")
        sys.exit(1)
    root = Tk()
    root.mainloop()
