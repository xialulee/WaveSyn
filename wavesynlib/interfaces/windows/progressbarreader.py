# -*- coding: utf-8 -*-
"""
Created on Fri Oct 23 10:21:48 2015

@author: Feng-cong Li
"""


from win32api       import SendMessage

PBM_GETRANGE = 1031
PBM_GETPOS   = 1032
        
class ProgressBarReader(object):
    def __init__(self, handle):
        self.__handle   = handle
        self.__rangeMax = SendMessage(handle, PBM_GETRANGE, 0, 0)
        
    @property
    def position(self):
        pos = SendMessage(self.__handle, PBM_GETPOS, 0, 0)
        return int(float(pos) / self.__rangeMax * 100)



from Tkinter                        import Tk
from wavesynlib.guicomponents       import tk as tktools
from wavesynlib.interfaces.timer.tk import TkTimer
from wavesynlib.common              import SimpleObserver
import sys

if __name__ == '__main__':
    handle  = sys.argv[1]
    if handle[:2] == '0x':
        handle = int(handle[2:], base=16)
    else:
        handle = int(handle)
        
    
    root     = Tk()
    tbIcon   = tktools.TaskbarIcon(root)
    pbReader = ProgressBarReader(handle)

    timer    = TkTimer()
    
    @SimpleObserver
    def observer(*args, **kwargs):
        tbIcon.progress = pbReader.position
        
    timer.addObserver(observer)
    timer.active = True
    
    root.mainloop()
    
    