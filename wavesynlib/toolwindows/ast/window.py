# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 00:45:09 2018

@author: Feng-cong Li
"""
import ast
import tkinter as tk

import hy 

from wavesynlib.widgets.tk.scrolledtree import ScrolledTree
from wavesynlib.widgets.tk.jsontotk import json_to_tk
from wavesynlib.widgets.tk.scrolledtext import ScrolledText
from wavesynlib.toolwindows.tkbasewindow import TkToolWindow
from wavesynlib.languagecenter.wavesynscript import Scripting, code_printer

import os
from pathlib import Path
# The following code generates the bytecode file of the 
# widgets.hy which is written in Hy.
# If we import a module written in hy directly in wavesyn,
# it will fail, and I cannot figure out why. 
import hy
try:
    from wavesynlib.toolwindows.ast.widgets import source_grp
except hy.errors.HyCompileError:
# After the bytecode file generated, we can import the module written by hy.    
    widgets_path = Path(__file__).parent / 'widgets.hy'
    os.system(f'hyc {widgets_path}')    
    from wavesynlib.toolwindows.ast.widgets import source_grp



opmap = {
    ast.Add: '+',
    ast.Sub: '-',
    ast.Mult: '*',
    ast.Div: '/',
    ast.Mod: '%',
    ast.LShift: '<<',
    ast.RShift: '>>',
    ast.BitOr: '|',
    ast.BitXor: '^',
    ast.BitAnd: '&'}



class ASTView:
    def __init__(self, *args, **kwargs):
        self.__tree_view = tree_view = ScrolledTree(*args, **kwargs)
        tree_view.tree['columns'] = ('value', 'type', 'lineno')
        tree_view.heading('value', text='Value')
        tree_view.heading('type', text='Type')
        tree_view.heading('lineno', text='Line No.')
        #tree_view.bind('<<TreeviewSelect>>', self._on_select_change)
        
        
    @property
    def tree_view(self):
        return self.__tree_view
    
    
    def clear(self):
        self.__tree_view.clear()
    
    
    def _add_node(self, obj, name=None, parent=None):
        type_name = type(obj).__name__
        lineno = getattr(obj, 'lineno', '')
        
        if isinstance(obj, (str, int, float)):
            value = str(obj)
        else:
            value = ''
            
        if parent is None:
            tree_node = self.__tree_view.insert('', 'end', text='module', values=(value, type_name, lineno))
        else:
            tree_node = self.__tree_view.insert(parent, 'end', text=name, values=(value, type_name, lineno))
            
        if isinstance(obj, list):
            for idx, elm in enumerate(obj):
                self._add_node(elm, f'{name}[{idx}]', tree_node)
            
        # Childs
        for attr_name in ('id', 'name', 'names', 'asname', 'module', 'n', 's', 'op',
                        'func', 'args', 'target', 
                        'attr', 
                        'bases',
                        'annotation',
                        'iter', 'test', 'body', 
                        'targets', 'orelse', 'left', 'right', 
                        'ops', 'comparators', 'value', 'values', 
                        'elts', 'keys'):
            if (not isinstance(obj, (list, str))) and hasattr(obj, attr_name):
                attr = getattr(obj, attr_name)
                self._add_node(attr, name=attr_name, parent=tree_node)
        


class ASTDisplay(TkToolWindow):
    window_name = 'WaveSyn-ASTDisplay'
    
    
    def __init__(self):
        super().__init__()
        
        tool_tabs = self._tool_tabs
        
        widgets_desc = [source_grp]
            
        tab = tk.Frame(tool_tabs)
        widgets = json_to_tk(tab, widgets_desc)
        widgets['parse_btn']['command'] = self._on_parse
        tool_tabs.add(tab, text='Code')
        
        self._make_window_manager_tab()
        
        tk_object = self.tk_object
        
        paned = tk.PanedWindow(tk_object)
        paned.config(sashwidth=4, sashrelief='groove', bg='forestgreen')
        paned.pack(expand='yes', fill='both')
        
        self.__textbox = textbox = ScrolledText(paned)
        paned.add(textbox, stretch='always')
        
        self.__tree_view = view = ASTView(paned)
        paned.add(view.tree_view, stretch='never')
        
        
    def load(self, tree):
        self.__tree_view.clear()
        self.__tree_view._add_node(tree)
        
        
    def _on_parse(self):
        code_text = self.__textbox.get_text()
        t = ast.parse(code_text)
        self.load(t)
