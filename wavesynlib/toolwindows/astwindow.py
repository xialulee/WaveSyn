# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 00:45:09 2018

@author: Feng-cong Li
"""
import ast
import tkinter as tk

from wavesynlib.widgets.tk import ScrolledText, ScrolledTree, json_to_tk
from wavesynlib.toolwindows.tkbasewindow import TkToolWindow
from wavesynlib.languagecenter.wavesynscript import Scripting, code_printer



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
        tree_view.tree['columns'] = ('value', 'prop', 'lineno')
        tree_view.heading('value', text='Value')
        tree_view.heading('prop', text='Prop')
        tree_view.heading('lineno', text='Line No.')
        #tree_view.bind('<<TreeviewSelect>>', self._on_select_change)
        
        
    @property
    def tree_view(self):
        return self.__tree_view
    
    
    def clear(self):
        self.__tree_view.clear()
    
    
    def _add_node(self, obj, prop_name='', parent=''):
        type_obj = type(obj)
        lineno = getattr(obj, 'lineno', '')
        
        if hasattr(obj, 'id'):
            values = (f'id: {obj.id}', prop_name, lineno)
        elif hasattr(obj, 'name'):
            values = (f'name: {obj.name}', prop_name, lineno)
        elif hasattr(obj, 'n'):
            values = (f'n: {obj.n}', prop_name, lineno)
        elif hasattr(obj, 's'): # Str
            values = (f's: {obj.s}', prop_name, lineno)
        elif hasattr(obj, 'op'):
            values = (f'op: {opmap[type(obj.op)]}', prop_name, lineno)
        else:
            values = ('', prop_name, lineno)
        
        tree_node = self.__tree_view.insert(
            parent,
            'end',
            text=type_obj.__name__,
            values=values)
        
        # Childs
        for attr_name in ('func', 'args', 'target', 
                        'iter', 'test', 'body', 
                        'targets', 'orelse', 'left', 'right', 
                        'ops', 'comparators', 'value', 'values', 
                        'elts', 'keys'):
            if hasattr(obj, attr_name):
                attr = getattr(obj, attr_name)
                if isinstance(attr, list):
                    for idx, item in enumerate(attr):
                        self._add_node(item, 
                                       prop_name=f'{attr_name}[{idx}]', 
                                       parent=tree_node)
                else:
                    self._add_node(attr, prop_name=attr_name, parent=tree_node)
        


class ASTDisplay(TkToolWindow):
    window_name = 'WaveSyn-ASTDisplay'
    
    
    def __init__(self):
        super().__init__()
        
        tool_tabs = self._tool_tabs
        
        widgets_desc = [
{'class':'Group', 'pack':{'side':'left', 'fill':'y'}, 'setattr':{'name':'Source'}, 'children':
    [{'class':'Button', 'config':{'text':'Parse', 'command':self._on_parse}}]}
]
            
        tab = tk.Frame(tool_tabs)
        json_to_tk(tab, widgets_desc)
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