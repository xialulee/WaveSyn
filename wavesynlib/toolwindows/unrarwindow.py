# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 20:38:27 2018

@author: Feng-cong Li
"""
import os
import tkinter
from pathlib import Path

from wavesynlib.widgets.tk import ScrolledTree, json_to_tk
from wavesynlib.toolwindows.tkbasewindow import TkToolWindow
from wavesynlib.interfaces.unrar.modelnode import list_content, get_content_tree
from wavesynlib.interfaces.unrar.modelnode import unpack as unpack_rar



class ContentTree:
    def __init__(self, *args, **kwargs):
        self.__tree_view = tree_view = ScrolledTree(*args, **kwargs)
        tree_view.tree['columns'] = ('ratio', 'crc', 'path')
        tree_view.heading('ratio', text='Ratio')
        tree_view.heading('crc', text='CRC')
        tree_view.heading('path', text='Path')
        
        
    @property
    def tree_view(self):
        return self.__tree_view
    
    
    def load(self, path):
        content_root = get_content_tree(list_content(path))
        content_root['Type'] = 'Directory'
        content_root['path'] = os.path.sep
        self._add_item('Archive', content_root)
            
        
    def _add_item(self, node_name, node, parent=''):
        if node['Type'] == 'Directory':
            values = ('', '', node['path'])
        else:
            values = (node['Ratio'], node['CRC32'], node['path'])
            
        node_id = self.tree_view.insert(
            parent, 
            'end', 
            text=node_name, 
            values=values)
        
        if 'children' in node:
            for child in node['children']:
                self._add_item(child, node['children'][child], parent=node_id)

    

class UnrarWindow(TkToolWindow):
    window_name = 'WaveSyn-UnRarWindow'
    
    def __init__(self):
        super().__init__()
        
        tool_tabs = self._tool_tabs
        widgets_desc = [
{'class':'Group', 'pack':{'side':'left', 'fill':'y'}, 'setattr':{'name':'Load'}, 'children':[
    {'class':'Button', 'config':{'text':'Load', 'command':self._on_load}}]
},

{'class':'Group', 'pack':{'side':'left', 'fill':'y'}, 'setattr':{'name':'Unpack'}, 'children':[
    {'class':'Button', 'config':{'text':'Unpack', 'command':self._on_unpack}}]
}
]
        tab = tkinter.Frame(tool_tabs)
        widgets = json_to_tk(tab, widgets_desc)
        tool_tabs.add(tab, text='Unrar')

        self._make_window_manager_tab()
        
        tk_object = self.tk_object
        self.__treeview = treeview = ContentTree(tk_object)
        treeview.tree_view.pack(expand='yes', fill='both')
        self.__path = None
        
        
    def load(self, rar_file:(str, Path)): # TO DO: support io.IOBase
        self.__treeview.load(rar_file)
        self.__path = rar_file
        
        
    def _on_load(self):
        pass
        
        
    def unpack(self, dir_path:(str, Path)):
        unpack_rar(self.__path, dir_path)
        
        
    def _on_unpack(self):
        pass
