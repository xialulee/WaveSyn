from wavesynlib.widgets.tk.taskbaricon import TaskbarIcon
from wavesynlib.interfaces.os.windows.shell.constants import TBPFLAG

import tkinter as tk
from tkinter import ttk
import threading
import win32con

from ctypes import byref, windll
from ctypes.wintypes import MSG
user32 = windll.user32

global numlock
numlock = False

global hotkey_id
hotkey_id = 1



def hotkey_thread_func(alt, ctrl, shift, key):
    modifiers = 0
    if alt:
        modifiers |= win32con.MOD_ALT
    if ctrl:
        modifiers |= win32con.MOD_CONTROL
    if shift:
        modifiers |= win32con.MOD_SHIFT
    user32.RegisterHotKey(None, hotkey_id, modifiers, key)
    msg = MSG()
    try:
        while user32.GetMessageW(byref(msg), None, 0, 0): 
            if msg.message == win32con.WM_HOTKEY:
                print("Hotkey.")
            elif msg.message == win32con.WM_USER:
                break
    finally:
        user32.UnregisterHotKey(None, hotkey_id)



class HotKeyFrame(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__key = tk.StringVar()
        entry_key = ttk.Entry(self, textvariable=self.__key)
        entry_key["width"] = 3
        entry_key.pack(side=tk.LEFT)

        self.__ctrl = tk.BooleanVar()
        self.__alt = tk.BooleanVar()
        self.__shift = tk.BooleanVar()
        
        check_ctrl = ttk.Checkbutton(self, text="Ctrl", variable=self.__ctrl)
        check_ctrl.pack(side=tk.LEFT)
        check_alt = ttk.Checkbutton(self, text="Alt", variable=self.__alt)
        check_alt.pack(side=tk.LEFT)
        check_shift = ttk.Checkbutton(self, text="Shift", variable=self.__shift)
        check_shift.pack(side=tk.LEFT)


    @property
    def key(self):
        return ord(self.__key.get().strip().upper())


    @property
    def ctrl(self):
        return self.__ctrl.get()

    @property
    def alt(self):
        return self.__alt.get()


    @property
    def shift(self):
        return self.__shift.get()
    



class KeyMapLabel(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self["borderwidth"] = 2
        self["relief"] = tk.GROOVE
        label_width = 1
        self.__label_old = tk.Label(self)
        self.__label_old["fg"] = "red"
        self.__label_old["width"] = label_width
        self.__label_old["font"] = ("Arial", 60)
        self.__label_old.pack(side=tk.LEFT)
        self.__label_new = tk.Label(self)
        self.__label_new["fg"] = "forestgreen"
        self.__label_new["width"] = label_width
        self.__label_new.pack(side=tk.LEFT, anchor=tk.SE)


    def show_key_map(self, old, new):
        self.__label_old["text"] = old
        self.__label_new["text"] = new



class NumpadFrame(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        old = [["7", "8", "9"], ["U", "I", "O"], ["J", "K", "L"], ["M", ",", "."]]
        new = [["7", "8", "9"], ["4", "5", "6"], ["1", "2", "3"], ["0", ",", "."]]

        for r in range(4):
            for c in range(3):
                label = KeyMapLabel(self)
                label.show_key_map(old=old[r][c], new=new[r][c])
                label.grid(row=r, column=c)



def main():
    root = tk.Tk()
    tb_icon = TaskbarIcon(root)
    tb_icon.progress = 0
    tk.Label(root, text="Numlock Hotkey:").pack(anchor=tk.W)
    htk = HotKeyFrame(root)
    htk.pack(anchor=tk.W)
    frm = NumpadFrame(root)
    frm.pack()

    thread_obj = None
    button_start = ttk.Button(root, text="Start")
    def on_start_click():
        nonlocal thread_obj
        button_text = button_start["text"]
        if button_text == "Start":
            button_start["text"] = "Stop"
            thread_obj = threading.Thread(target=hotkey_thread_func, 
                args=(htk.alt, htk.ctrl, htk.shift, htk.key))
            thread_obj.setDaemon(True)
            thread_obj.start()
            tb_icon.state = TBPFLAG.TBPF_NORMAL
            tb_icon.progress = 100
        elif button_text == "Stop":
            button_start["text"] = "Start"
            user32.PostThreadMessageW(thread_obj.ident, win32con.WM_USER, 0, None)
            thread_obj = None
            tb_icon.state = TBPFLAG.TBPF_NORMAL
            tb_icon.progress = 0
    button_start["command"] = on_start_click
    button_start.pack(anchor=tk.E)
    root.mainloop()



if __name__ == "__main__":
    main()