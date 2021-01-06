#!/usr/bin/env python

# memstatus.pyw
# 2013.09.21 AM 11:38
# win8 python27
# Feng-cong Li

#import os
from pathlib import Path
from tkinter import Tk, Label
import ctypes as ct

from wavesynlib.widgets.tk.taskbaricon import TaskbarIcon
from wavesynlib.interfaces.timer.tk import TkTimer
from wavesynlib.interfaces.os.windows.shell.constants import TBPFLAG
from wavesynlib.interfaces.os.windows.processes.utils import singleton
from wavesynlib.interfaces.os.windows.memstatus import get_memory_usage

APPID = '129832A8-AA09-4416-8C6A-9945FAB4CDFA'



def main():
    if not singleton(APPID):
        return 
    
    ct.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APPID)
    root    = Tk()
    root.iconbitmap(default=Path(__file__).parent / 'memmeter.ico')
    label   = Label()
    label.pack()
    tbIcon  = TaskbarIcon(root) 
    
    timer = TkTimer(widget=root, interval=2000) # No Config Dialog
    
    @timer.add_observer   
    def show_memory_usage(event=None):
        memusage = get_memory_usage()
        label['text']   = f'Memory Usage: {memusage}%'
        root.title(f'RAM {memusage}%')
        tbIcon.progress = memusage        
        if memusage <= 60:
            state = TBPFLAG.TBPF_NORMAL
        elif 60 <= memusage < 80:
            state = TBPFLAG.TBPF_PAUSED
        else:
            state = TBPFLAG.TBPF_ERROR
        tbIcon.state = state

    timer.active = True
    root.mainloop()



if __name__ == '__main__':
    main()
