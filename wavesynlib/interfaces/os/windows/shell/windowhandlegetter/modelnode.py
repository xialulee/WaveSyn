# -*- coding: utf-8 -*-
"""
Created on Mon Oct  1 23:01:04 2018

@author: Feng-cong Li
"""

from . import utils as hwnd_getter
from wavesynlib.languagecenter.wavesynscript import ModelNode, constant_handler



class _GetterConstants(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
    @constant_handler(doc="""\
The handle of the console. For functionalities which need an arbitrary
window handle.                       
""")
    def constant_handler_HWND_ARBITRARY(self, arg, **kwargs):
        return self.parent_node.arbitrary()
    
    
    @constant_handler(doc="""\
The handle of the foreground window.
""")
    def constant_handler_HWND_FOREGROUND(self, arg, **kwargs):
        return self.parent_node.foreground()
    
        
    @constant_handler(doc="""\
The handle of the window on which the mouse cursor is.
""")
    def constant_handler_HWND_WINDOW_FROM_CURSOR_POS(self, arg, **kwargs):
        return self.parent_node.from_cursor_pos(toplevel=True)
    

    @constant_handler(doc="""\
The handle of the window on which the mouse cursor is.
""")
    def constant_handler_HWND_CONTROL_FROM_CURSOR_POS(self, arg, **kwargs):
        return self.parent_node.from_cursor_pos(toplevel=False)    



class WindowHandleGetter(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.constants = _GetterConstants()
        
        
    def foreground(self):
        return hwnd_getter.get_foreground()
    
    
    def arbitrary(self):
        return self.root_node.gui.root_handle
    
    
    def from_point(self, x, y, toplevel=True):
        return hwnd_getter.get_hwnd_from_point(x, y, toplevel)
        
        
    def from_cursor_pos(self, toplevel=True):
        return hwnd_getter.get_hwnd_from_cursor_pos(toplevel)
