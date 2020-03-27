# -*- coding: utf-8 -*-
"""
Created on Fri Oct 23 10:21:48 2015

@author: Feng-cong Li
"""
from __future__ import print_function
from __future__ import division

from win32api   import SendMessage

PBM_GETRANGE = 1031
PBM_GETPOS   = 1032
        
class ProgressBarReader(object):
    def __init__(self, handle):
        self.__handle   = handle
        self.__rangeMax = SendMessage(handle, PBM_GETRANGE, 0, 0)
        
    @property
    def position(self):
        pos = SendMessage(self.__handle, PBM_GETPOS, 0, 0)
        return pos * 100 // self.__rangeMax



from tkinter import Tk
from wavesynlib.widgets.tk.taskbaricon import TaskbarIcon
from wavesynlib.interfaces.timer.tk import TkTimer
import sys


import ctypes as ct
APPID = 'wavesyn.interfaces.windows.progressbarreader'

if __name__ == '__main__':
    ct.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APPID)
    handle  = sys.argv[1]
    if handle[:2] == '0x':
        handle = int(handle[2:], base=16)
    else:
        handle = int(handle)
        
    root     = Tk()
    tbIcon   = TaskbarIcon(root)
    pbReader = ProgressBarReader(handle)

    timer    = TkTimer()

    @timer.add_observer    
    def observer(*args, **kwargs):
        tbIcon.progress = pbReader.position
        
    timer.active = True
    
    root.mainloop()
    
