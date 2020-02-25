# -*- coding: utf-8 -*-
"""
Created on Fri Jun 09 22:58:03 2017

@author: Feng-cong Li
"""
import sys
from tkinter import Tk, Label
import ctypes as ct
import time

from wavesynlib.widgets import tk as tktools
from wavesynlib.widgets.taskbaricon import TaskbarIcon
from wavesynlib.interfaces.timer.tk import TkTimer
from wavesynlib.interfaces.os.windows.shell.constants import TBPFLAG

APPID = u'548CEA05-47A1-455C-9332-11F6560865F3'



def main(argv):
    ct.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APPID+str(time.time()))
    root = Tk()
    label = Label(root)
    label.pack()
    tb_icon = TaskbarIcon(root)
    
    total = int(argv[1])
    current = [0]
    
    timer = TkTimer(widget=root, interval=1000)
    
    @timer.add_observer
    def show_left():
        current[0] += 1
        percent = int(current[0] / total * 100)
        tb_icon.progress = percent
        label['text'] = '{} seconds left.'.format(total-current[0])
        if 0 <= percent <= 50:
            state = TBPFLAG.TBPF_NORMAL
        elif 50 < percent <= 80:
            state = TBPFLAG.TBPF_PAUSED
        else:
            state = TBPFLAG.TBPF_ERROR
        tb_icon.state = state
        if current[0] >= total:
            timer.active = False
            tb_icon.state = TBPFLAG.TBPF_NOPROGRESS
        
    timer.active = True
    root.mainloop()
    
    
    
if __name__ == '__main__':
    main(sys.argv)
