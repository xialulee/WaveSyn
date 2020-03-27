# -*- coding: utf-8 -*-
"""
Created on Sun Oct 15 23:25:03 2017

@author: Feng-cong Li
"""
from tkinter import Frame

import hy
from wavesynlib.toolwindows.tkbasewindow import TkToolWindow
from wavesynlib.widgets.tk.scrolledtree import ScrolledTree



class ControlTreeview(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
    def _make_widgets(self):
        tree_container = ScrolledTree(self)
        tree_container.pack(expand='yes', fill='both')
        self.__tree = tree = tree_container.tree
        tree['columns'] = ['value', 'action']
        tree.heading('value', text='Value')
        tree.heading('action', text='Action')
        
        
        
class JoystickManageWindow(TkToolWindow):
    window_name = 'WaveSyn-JoystickManager'
    
    
    def __init__(self):
        super().__init__()
        self._make_window_manager_tab()
        self.__treeview = treeview = ControlTreeview(self.tk_object)
        treeview.pack(expand='yes', fill='both')