#!/usr/bin/env python

# memstatus.pyw
# 2013.09.21 AM 11:38
# win8 python27
# Feng-cong Li

import os

from tkinter import Tk, Label
import ctypes as ct

from wavesynlib.guicomponents import tk as tktools
from wavesynlib.interfaces.timer.tk import TkTimer
from wavesynlib.interfaces.os.windows.shell.constants import TBPFLAG
from wavesynlib.interfaces.os.windows.process import singleton
from wavesynlib.languagecenter.utils import get_caller_dir



class MEMORYSTATUS(ct.Structure):
    _fields_    = [
        ('dwLength',        ct.wintypes.DWORD),
        ('dwMemoryLoad',    ct.wintypes.DWORD),
        ('dwTotalPhys',     ct.c_size_t),
        ('dwAvailPhys',     ct.c_size_t),
        ('dwTotalPageFile', ct.c_size_t),
        ('dwAvailPageFile', ct.c_size_t),
        ('dwTotalVirtual',  ct.c_size_t),
        ('dwAvailVirtual',  ct.c_size_t)
    ]
    
    
    
def get_memory_usage():
    memstat = MEMORYSTATUS()
    memstat.dwLength = ct.sizeof(MEMORYSTATUS)    
    ct.windll.kernel32.GlobalMemoryStatus(ct.byref(memstat))
    memusage = memstat.dwMemoryLoad
    return memusage      



APPID = '129832A8-AA09-4416-8C6A-9945FAB4CDFA'



def main():
    if not singleton(APPID):
        return 
    
    ct.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APPID)
    root    = Tk()
    root.iconbitmap(default=os.path.join(get_caller_dir(), 'memmeter.ico'))
    label   = Label()
    label.pack()
    tbIcon  = tktools.TaskbarIcon(root) 
    
    timer = TkTimer(widget=root, interval=2000) # No Config Dialog
    
    @timer.add_observer   
    def show_memory_usage():
        memusage = get_memory_usage()
        label['text']   = f'Memory Usage: {memusage}%'
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
