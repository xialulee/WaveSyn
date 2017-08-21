# 2010.3.9 Created by Feng-cong Li

from tkinter import Tk, Frame, IntVar
from tkinter.ttk import Checkbutton
import  ctypes as ct
import  tkinter.messagebox as msgbox
import  sys

hKHook = [0]

HC_ACTION       =   0
WM_KEYDOWN      =   0x100
WM_SYSKEYDOWN   =   0x104
WM_KEYUP        =   0x101
WM_SYSKEYUP     =   0x105
VK_TAB          =   0x9
LLKHF_ALTDOWN   =   0x20
VK_ESCAPE       =   0x1B
VK_CONTROL      =   0x11

GetKeyState         = ct.windll.user32.GetKeyState
SetWindowsHookExA   = ct.windll.user32.SetWindowsHookExA
CallNextHookEx      = ct.windll.user32.CallNextHookEx
GetModuleHandleA    = ct.windll.kernel32.GetModuleHandleA

key_name = {}
key_name['LWIN'] = 'Left Win'
key_name['RWIN'] = 'Right Win'
key_name['MENU'] = 'Menu'
key_name['ALT+ESC'] = 'ALT+ESC'
key_name['ALT+TAB'] = 'ALT+TAB'
key_name['CTRL+ESC'] = 'CTRL+ESC'

key_stat = {}


# hook functions
class KBDLLHOOKSTRUCT(ct.Structure):
	_fields_ = [('vkCode',		ct.c_int),
				('scanCode',	ct.c_int),
				('flags',		ct.c_int),
				('time',		ct.c_int),
				('dwExtraInfo',	ct.c_int)]
    
    

def khook_proc(nCode, wParam, lParam):
    eat = False
    vkCode  = lParam.contents.vkCode
    flags   = lParam.contents.flags
    if key_stat['LWIN'].get():
        if vkCode == 91: eat = True
    if key_stat['RWIN'].get():
        if vkCode == 92: eat = True
    if key_stat['MENU'].get():
        if vkCode == 93: eat = True
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
        return CallNextHookEx(hKHook[0], nCode, wParam, lParam)
    
    

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
    KHOOK = ct.WINFUNCTYPE(ct.c_int, ct.c_int, ct.c_int, ct.POINTER(KBDLLHOOKSTRUCT))
    c_khook = KHOOK(khook_proc)
    hKHook[0] = SetWindowsHookExA(13, c_khook, GetModuleHandleA(0), 0)
    if not hKHook[0]:
        msgbox.showerror('Error', "Can't hook keyboard.")
        sys.exit(1)
    root = Tk()
    mainw = MainWin()
    root.title('DKey')
    root.mainloop()