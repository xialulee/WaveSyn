# -*- coding: utf-8 -*-
"""
Created on Thu Mar 15 10:41:55 2018

@author: Feng-cong Li
"""
from pathlib import Path
from tkinter import Tk, Label
from ctypes import windll
GetKeyState = windll.user32.GetKeyState

from wavesynlib.widgets.tk.taskbaricon import TaskbarIcon
from wavesynlib.interfaces.timer.tk import TkTimer
from wavesynlib.interfaces.os.windows.shell.constants import TBPFLAG
from wavesynlib.interfaces.os.windows.processes.utils import singleton

    

# comtypes.GUID.create_new()    
APPID = "63F4CDB1-69E9-4DDF-81D4-4FE77803278F"

def main():
    if not singleton(APPID):
        return 
    
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(APPID)
    my_dir = Path(__file__).parent
    ico = my_dir/'numlock.ico'
    
    root = Tk()
    root.title('NumLock')
    root.iconbitmap(default=ico)
    tb_icon  = TaskbarIcon(root)
    tb_icon.state = TBPFLAG.TBPF_NORMAL
    label = Label(root)
    label.pack()
    
    timer = TkTimer(widget=root, interval=250)
    
    @timer.add_observer
    def show_numlock(event=None):
        if GetKeyState(0x90) & 0xffff:
            label['text'] = 'On'
            tb_icon.progress = 100
        else:
            label['text'] = 'Off'
            tb_icon.progress = 0
            
    timer.active = True
    root.mainloop()
    
    
    
if __name__ == '__main__':
    main()
    
            
            