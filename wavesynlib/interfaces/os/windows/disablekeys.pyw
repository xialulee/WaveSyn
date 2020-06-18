# 2010.3.9 Created by Feng-cong Li

from tkinter import Tk, Frame, IntVar
from tkinter.ttk import Checkbutton
import  ctypes as ct
import  tkinter.messagebox as msgbox
import  sys
import atexit

from wavesynlib.languagecenter.datatypes.wintypes.hook import (
    KHOOKPROC)

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
    VK_CONTROL)

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

    

def khook_proc(nCode, wParam, lParam):
    global hKHook
    eat = False
    vkCode  = lParam.contents.vkCode
    flags   = lParam.contents.flags
    if key_stat['LWIN'].get():
        if vkCode == VK_LWIN: eat = True
    if key_stat['RWIN'].get():
        if vkCode == VK_RWIN: eat = True
    if key_stat['MENU'].get():
        if vkCode == VK_APPS: eat = True
    if key_stat['ALT+ESC'].get():
        if vkCode == VK_ESCAPE and flags & LLKHF_ALTDOWN != 0:
            eat = True
    if key_stat['ALT+TAB'].get():
        if vkCode == VK_TAB and flags & LLKHF_ALTDOWN != 0:
            eat = True
    if key_stat['CTRL+ESC'].get():
        if vkCode == VK_ESCAPE and GetKeyState(VK_CONTROL) and 0x8000:
            eat = True
    if eat:
        return -1
    else:
        return CallNextHookEx(hKHook, nCode, wParam, lParam)
    
    

# gui classes
class Column(Frame):
    def __init__(self, parent = None):
        Frame.__init__(self, parent)
        self.__parent = parent
        

class MainWin(Frame):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.pack()
            
        for idx, name in enumerate(['LWIN', 'RWIN', 'MENU', 'ALT+ESC', 'ALT+TAB', 'CTRL+ESC']):
            key_stat[name] = IntVar(0)
            Checkbutton(self, text=key_name[name], variable=key_stat[name], width=10).grid(row=idx%3, column=idx//3)
            
            

if __name__ == '__main__':
    c_khook = KHOOKPROC(khook_proc)
    hKHook = SetWindowsHookExA(WH_KEYBOARD_LL, c_khook, None, 0)
    if not hKHook:
        msgbox.showerror('Error', "Can't hook keyboard.")
        sys.exit(1)
    
    @atexit.register
    def on_exit():
        UnhookWindowsHookEx(hKHook)

    root = Tk()
    mainw = MainWin()
    root.title('DKey')
    root.mainloop()