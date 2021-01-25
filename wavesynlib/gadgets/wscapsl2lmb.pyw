from tkinter import Tk, Frame, IntVar
from tkinter.ttk import Checkbutton
import  ctypes as ct
import  tkinter.messagebox as msgbox
import  sys
import atexit

from wavesynlib.languagecenter.datatypes.wintypes.hook import (
    KHOOKPROC)
from wavesynlib.interfaces.os.windows.inputsender.utils import send_mouse_input

global hKHook

from win32con import (
    HC_ACTION,
    WM_KEYDOWN,
    WM_SYSKEYDOWN,
    WM_KEYUP,
    WM_SYSKEYUP,
    WH_KEYBOARD_LL,
    VK_TAB,
    VK_LWIN,
    VK_RWIN,
    VK_APPS,
    LLKHF_ALTDOWN,
    VK_ESCAPE,
    VK_CONTROL,
    VK_CAPITAL)

GetKeyState         = ct.windll.user32.GetKeyState
SetWindowsHookExA   = ct.windll.user32.SetWindowsHookExA
UnhookWindowsHookEx = ct.windll.user32.UnhookWindowsHookEx
CallNextHookEx      = ct.windll.user32.CallNextHookEx

key_name = {}
key_name['LWIN'] = 'Left Win'
key_name['RWIN'] = 'Right Win'
key_name['MENU'] = 'Menu'
key_name['ALT+ESC'] = 'ALT+ESC'
key_name['ALT+TAB'] = 'ALT+TAB'
key_name['CTRL+ESC'] = 'CTRL+ESC'

key_stat = {}



def khook_proc(nCode, wParam, lParam, previous=[None]):
    global hKHook
    vkCode  = lParam.contents.vkCode

    kwargs = {}
    capsl  = False

    if vkCode == VK_CAPITAL:
        capsl = True
        if wParam == previous[0]:
            pass
        else:
            kwargs = {
                "dx":     0,
                "dy":     0,
                "button": "left"}
            if wParam == WM_KEYDOWN:
                kwargs["press"] = True
            elif wParam == WM_KEYUP:
                kwargs["release"] = True
            else:
                raise ValueError("wParam not supported.")
            previous[0] = wParam

    if capsl:
        if kwargs:
            send_mouse_input(**kwargs)
        return -1
    else:
        return CallNextHookEx(hKHook, nCode, wParam, lParam)
    


if __name__ == '__main__':
    c_khook = KHOOKPROC(khook_proc)
    hKHook = SetWindowsHookExA(WH_KEYBOARD_LL, c_khook, None, 0)
    if not hKHook:
        msgbox.showerror('Error', "Can't hook keyboard.")
        sys.exit(1)
    
    atexit.register(lambda: UnhookWindowsHookEx(hKHook))

    root = Tk()
    root.mainloop()