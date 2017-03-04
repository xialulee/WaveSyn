# -*- coding: utf-8 -*-
"""
Created on Sat Mar 04 16:08:52 2017

@author: Feng-cong Li
"""

import os

from six.moves.tkinter import *
from comtypes import *
import ctypes as ct

import psutil

from wavesynlib.guicomponents import tk as tktools
from wavesynlib.interfaces.timer.tk import TkTimer
from wavesynlib.interfaces.os.windows.shell.constants import TBPFLAG
from wavesynlib.languagecenter.utils import get_caller_dir

    
    
def get_cpu_usage():
    return psutil.cpu_percent()


APPID = 'wavesyn/windows_apps/cpustatus'

def main():
    ct.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APPID)
    root    = Tk()
    root.iconbitmap(default=os.path.join(get_caller_dir(), 'cpumeter.ico'))
    label   = Label()
    label.pack()
    tb_icon  = tktools.TaskbarIcon(root) 
    
    timer = TkTimer(widget=root, interval=2000) # No Config Dialog
    
    @timer.add_observer   
    def show_memory_usage():
        cpu_usage = get_cpu_usage()
        label['text']   = 'CPU Usage: {}%'.format(cpu_usage)
        tb_icon.progress = cpu_usage        
        if cpu_usage <= 60:
            state = TBPFLAG.TBPF_NORMAL
        elif 60 <= cpu_usage < 80:
            state = TBPFLAG.TBPF_PAUSED
        else:
            state = TBPFLAG.TBPF_ERROR
        tb_icon.state = state

    timer.active = True
    root.mainloop()


if __name__ == '__main__':
    main()
