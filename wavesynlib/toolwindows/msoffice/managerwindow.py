# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 15:33:03 2017

@author: Feng-cong Li
"""

from __future__ import print_function, division, unicode_literals

import six.moves.tkinter as tk
import six.moves.tkinter_ttk as ttk

from wavesynlib.guicomponents.tk import ScrolledTree, Group
from wavesynlib.toolwindows.tkbasewindow import TkToolWindow



class AppTreeview(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self._make_widgets()
        
        
    def _make_widgets(self):
        tree_container = ScrolledTree(self)
        tree_container.pack(expand='yes', fill='both')
        self.__tree = tree = tree_container.tree
        tree['columns'] = ['app', 'id']
        tree.heading('app', text='App')
        tree.heading('id', text='ID')
        
        
    def update(self, app_info):
        self.clear()
        for app, id_ in app_info:
            self.__tree.insert('', 'end', values=(app, id_))
            
            
    def clear(self):
        tree = self.__tree
        for row in tree.get_children():
            tree.delete(row)
            
            
            
class OfficeManager(TkToolWindow):
    window_name = 'WaveSyn-OfficeManager'
    
    
    def __init__(self):
        TkToolWindow.__init__(self)
        self._gui_images = []
        self._make_window_manager_tab()
        self.__treeview = treeview = AppTreeview(self.tk_object)
        treeview.pack(expand='yes', fill='both')