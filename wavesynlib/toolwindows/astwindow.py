# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 00:45:09 2018

@author: Feng-cong Li
"""
from wavesynlib.guicomponents.tk import ScrolledText, ScrolledTree
from wavesynlib.languagecenter.wavesynscript import Scripting, code_printer



class ASTView:
    def __init__(self, *args, **kwargs):
        self.__tree_view = tree_view = ScrolledTree(*args, **kwargs)
        tree_view.tree['columns'] = ('type',)
        tree_view.heading('value', text='Type')
        tree_view.bind('<<TreeviewSelect>>', self._on_select_change)
        
        
    @property
    def tree_view(self):
        return self.__tree_view
    
    
    def _add_item(self, name, obj, parent=''):
        type_obj = type(obj)
        
        tree_node = self.__tree_view.insert(
            parent,
            'end',
            text=name,
            values=(type_obj.__name__,))
        
        # Childs
        if isinstance(obj, (ast.stmt, ast.expr, ast.mod)):
            pass
        if isinstance(obj, list):
            pass
