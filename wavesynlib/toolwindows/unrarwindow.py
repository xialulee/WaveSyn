# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 20:38:27 2018

@author: Feng-cong Li
"""
import os

from wavesynlib.widgets.tk import ScrolledTree
from wavesynlib.interfaces.unrar.modelnode import list_contents



class ContentTree:
    def __init__(self, *args, **kwargs):
        self.__tree_view = tree_view = ScrolledTree(*args, **kwargs)
        tree_view.tree['columns'] = ('ratio', 'crc')
        tree_view.heading('ratio', text='Ratio')
        tree_view.heading('crc', text='CRC')
        self.__dir = {}
        self.__contents = None
        
        
    @property
    def tree_view(self):
        return self.__tree_view
    
    
    def load(self, path):
        self.__contents = contents = list_contents(path)
        for item in contents:
            pass
        
        
    def _add_item(self, item):
        name = item['name']
        path_item = os.path.split(name)
        tree_node = self.tree_view.insert(
            parent,
            'end',
            text=name,
            values=(item['Ratio'], item['CRC']))
    
    
    def _get_dir_node(self, path):
        node_dict = self.__dir
        for d in path:
            if d not in node_dict:
                pass