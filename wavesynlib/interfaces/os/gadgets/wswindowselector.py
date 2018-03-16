# -*- coding: utf-8 -*-
"""
Created on Fri Oct 30 13:07:27 2015

@author: Feng-cong Li
"""
import sys
import getopt


from ctypes.wintypes import DWORD, POINT, RECT
from ctypes import byref, windll
WindowFromPoint = windll.user32.WindowFromPoint
GetCursorPos = windll.user32.GetCursorPos
GetParent = windll.user32.GetParent
GetWindowRect = windll.user32.GetWindowRect
GetWindowThreadProcessId = windll.user32.GetWindowThreadProcessId

from tkinter import Tk, Button

from wavesynlib.interfaces.timer.tk import TkTimer



class WindowSelector:
    def __init__(self):
        self.__root = root = Tk()
        self.__root.wm_attributes('-topmost', True)
        self.__sel_button = sel_button = Button(root, text='Select', command=self.on_select)
        sel_button.pack()
        self.__sel_window = None
        self.__cancel = True 
        self.__timer = TkTimer()
        
    def on_select(self):
        self.__cancel = False
        self.__timer.active = False
        self.__root.quit()
        
        
    def mainloop(self):
        cursor_pos  = POINT()
        window_rect = RECT()
        self_handle = self.__root.winfo_id()
        self_rect   = RECT()        
        
        timer      = self.__timer
        
        @timer.add_observer
        def get_window(*args, **kwargs):
            GetCursorPos(byref(cursor_pos))
            handle = WindowFromPoint(cursor_pos)            
            GetWindowRect(self_handle, byref(self_rect))
            if not (
                    cursor_pos.y >= self_rect.top and \
                    cursor_pos.x >= self_rect.left and \
                    cursor_pos.y <= self_rect.bottom and \
                    cursor_pos.x <= self_rect.right) and \
                    (handle != GetParent(self_handle)):                
                self.__sel_window = handle                
                GetWindowRect(handle, byref(window_rect))
                self.__root.geometry(f'+{max(0, window_rect.left)}+{max(0, window_rect.top)}')               

        timer.interval = 500
        timer.active = True
        self.__root.mainloop()
        
    @property
    def selected_window(self):
        if self.__cancel:
            return None
        else:
            return self.__sel_window
        
        
    @property
    def selected_top(self):
        h1 = self.selected_window
        while True:
            h2 = GetParent(h1)
            if not h2:
                break
            h1 = h2
        return h1
    
            
    @property
    def selected_process(self):
        pid = DWORD()
        if self.selected_window:
            GetWindowThreadProcessId(self.selected_window, byref(pid))
            return pid.value
        else:
            return None
            
        
        
def main(argv):
    try:
        opts, args = getopt.getopt(argv[1:], 'pt', ['handle', 'pid', 'top'])
    except getopt.GetoptError as err:
        print(str(err), file=sys.stderr)
        return 1
        
    win = WindowSelector()
    win.mainloop()
                
    for o, a in opts:
        if o in ('-p', '--pid'):
            print(win.selected_process)
        elif o in ('--handle',):
            print(win.selected_window)
        elif o in ('-t', '--top'):
            print(win.selected_top)
        
    
    
if __name__ == '__main__':
    sys.exit(main(sys.argv))