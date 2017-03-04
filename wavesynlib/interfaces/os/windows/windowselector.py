# -*- coding: utf-8 -*-
"""
Created on Fri Oct 30 13:07:27 2015

@author: Feng-cong Li
"""
from __future__ import print_function

import sys
import getopt


from ctypes.wintypes import DWORD, POINT, RECT
from ctypes          import byref, windll
WindowFromPoint             = windll.user32.WindowFromPoint
GetCursorPos                = windll.user32.GetCursorPos
GetParent                   = windll.user32.GetParent
GetWindowRect               = windll.user32.GetWindowRect
GetWindowThreadProcessId    = windll.user32.GetWindowThreadProcessId


from six.moves.tkinter import *

from wavesynlib.interfaces.timer.tk           import TkTimer
from wavesynlib.languagecenter.utils          import eval_format

class WindowSelector(object):
    def __init__(self):
        self.__root = root = Tk()
        self.__root.wm_attributes('-topmost', True)
        self.__selButton   = selButton = Button(root, text='Select', command=self.onSelect)
        selButton.pack()
        self.__selWindow   = None
        self.__cancel      = True 
        self.__timer       = TkTimer()
        
    def onSelect(self):
        self.__cancel       = False
        self.__timer.active = False
        self.__root.quit()
        
        
    def mainloop(self):
        cursorPos  = POINT()
        windowRect = RECT()
        selfHandle = self.__root.winfo_id()
        selfRect   = RECT()        
        
        timer      = self.__timer
        
        @timer.add_observer
        def getWindow(*args, **kwargs):
            GetCursorPos(byref(cursorPos))
            handle = WindowFromPoint(cursorPos)            
            GetWindowRect(selfHandle, byref(selfRect))
            if not (cursorPos.y >= selfRect.top and cursorPos.x >= selfRect.left and cursorPos.y <= selfRect.bottom and cursorPos.x <= selfRect.right) and (handle != GetParent(selfHandle)):                
                self.__selWindow = handle                
                GetWindowRect(handle, byref(windowRect))
                self.__root.geometry(eval_format('+{max(0, windowRect.left)}+{max(0, windowRect.top)}'))                

        timer.interval = 500
        timer.active = True
        self.__root.mainloop()
        
    @property
    def selectedWindow(self):
        if self.__cancel:
            return None
        else:
            return self.__selWindow
            
    @property
    def selectedProcess(self):
        pid = DWORD()
        if self.selectedWindow:
            GetWindowThreadProcessId(self.selectedWindow, byref(pid))
            return pid.value
        else:
            return None
            
        
        
def main(argv):
    try:
        opts, args = getopt.getopt(argv[1:], 'hp', ['hwnd', 'pid'])
    except getopt.GetoptError as err:
        print(str(err), file=sys.stderr)
        return 1
        
    win = WindowSelector()
    win.mainloop()
                
    for o, a in opts:
        if o in ('-p', '--pid'):
            print(win.selectedProcess)
        elif o in ('-h', '--hwnd'):
            print(win.selectedWindow)
        
    
    
if __name__ == '__main__':
    sys.exit(main(sys.argv))