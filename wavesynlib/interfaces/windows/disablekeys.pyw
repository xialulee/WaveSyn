# 2010.3.9 Created by Feng-cong Li

from    Tkinter import *
import  ctypes as ct
import  tkMessageBox as msgbox
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
key_stat['LWIN'] = False
key_stat['RWIN'] = False
key_stat['MENU'] = False
key_stat['ALT+ESC'] = False
key_stat['ALT+TAB'] = False
key_stat['CTRL+ESC'] = False

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
    if key_stat['LWIN']:
        if vkCode == 91: eat = True
    if key_stat['RWIN']:
        if vkCode == 92: eat = True
    if key_stat['MENU']:
        if vkCode == 93: eat = True
    if key_stat['ALT+ESC']:
        if vkCode == VK_ESCAPE and flags & LLKHF_ALTDOWN != 0:
            eat = True
    if key_stat['ALT+TAB']:
        if vkCode == VK_TAB and flags & LLKHF_ALTDOWN != 0:
            eat = True
    if key_stat['CTRL+ESC']:
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
    def __init__(self, parent=None, **args):
        Frame.__init__(self, parent, args)
        self.pack()
        c1 = Frame(self)
        c2 = Frame(self)
        c1.pack(side=LEFT, expand=YES, fill=Y)
        c2.pack(side=LEFT, expand=YES, fill=Y)
        def reverse(key):
            def func():
                key_stat[key] = not key_stat[key]
            return func
        for i in ['LWIN', 'RWIN', 'MENU']:
            item = Frame(c1)
            item.pack(side=TOP,expand=YES,fill=X)
            Checkbutton(item, text=key_name[i],\
                        command=reverse(i)).pack(side=LEFT)
        for i in ['ALT+ESC', 'ALT+TAB', 'CTRL+ESC']:
            item = Frame(c2)
            item.pack(side=TOP,expand=YES,fill=X)
            Checkbutton(item, text=key_name[i],\
                        command=reverse(i)).pack(side=LEFT)

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