# -*- coding: utf-8 -*-
"""
Created on Mon Oct  1 18:24:20 2018

@author: Feng-cong Li
"""

from ctypes import windll, byref
from ctypes.wintypes import POINT

GetCursorPos = windll.user32.GetCursorPos
GetParent = windll.user32.GetParent
WindowFromPoint = windll.user32.WindowFromPoint

from wavesynlib.languagecenter.wavesynscript import ModelNode, constant_handler



class WSScriptConstants(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
    @constant_handler(doc='''\
The handle of the console. For functionalities which need an arbitrary
window handle.                       
''')
    def hwnd_arbitrary(self, arg, **kwargs):
        return self.root_node.gui.root_handle
    
    
    @constant_handler(doc='''\
The handle of the foreground window.
''')
    def hwnd_foreground(self, arg, **kwargs):
        return windll.user32.GetForegroundWindow()
    
    
    @constant_handler(doc='''\
The handle of the window on which the mouse cursor is.
''')
    def hwnd_from_cursor_pos(self, arg, **kwargs):
        cursor_pos = POINT()
        GetCursorPos(byref(cursor_pos))
        h1 = WindowFromPoint(cursor_pos)
        while True:
            h2 = GetParent(h1)
            if not h2:
                break
            h1 = h2
        return h1
        