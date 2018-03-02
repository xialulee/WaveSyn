# -*- coding: utf-8 -*-
"""
Created on Sun Jan 10 16:55:14 2016

@author: Feng-cong Li
"""
from importlib import import_module

from wavesynlib.languagecenter.wavesynscript import (
    ModelNode, NodeDict, Scripting)
from wavesynlib.languagecenter.designpatterns import Observable
from wavesynlib.languagecenter.datatypes import TypeLinks



class BaseWindowNode(ModelNode):
    pass



class WindowID(TypeLinks):
    def get_link_info(self):
        return (('Foreground', lambda *args, **kwargs: self.foreground()),)
    
    
    def __init__(self, node):
        self.__id = id(node)
        self.__node = node
        
        
    @property
    def node_id(self):
        return self.__id
    
    
    @property
    def node_object(self):
        return self.__node
    
    
    def __int__(self):
        return self.__id
    
    
    def __repr__(self):
        return f'<WindowID: ID={self.node_id}>'
    
    
    def foreground(self):
        self.__node.tk_object.deiconify()



class WindowDict(NodeDict, Observable):
    def __init__(self, node_name=''):
        NodeDict.__init__(self, node_name=node_name)
        Observable.__init__(self)
        
                
    def __setitem__(self, key, val):
        if isinstance(key, WindowID):
            key = key.node_id
        if not isinstance(val, BaseWindowNode):
            raise TypeError(f"{self.node_path} only accepts instance of BaseWindowNode's subclasses.")
        if key != id(val):
            raise ValueError('The key should be identical to the ID of the window.')
        NodeDict.__setitem__(self, key, val)
        self.notify_observers(val, 'new')
        
        
    def __getitem__(self, key):
        if isinstance(key, WindowID):
            key = key.node_id
        return NodeDict.__getitem__(self, key)
    
    
    def __delitem__(self, key):
        if isinstance(key, WindowID):
            key = key.node_id
        return NodeDict.__delitem__(self, key)
        
        
    @Scripting.printable
    def create(self, module_name, class_name):
        mod = import_module(module_name)
        return self.add(node=getattr(mod, class_name)())  
      
        
    def add(self, node):
        self[id(node)] = node
        return WindowID(node)
    
        
    def pop(self, key):
        if isinstance(key, WindowID):
            key = key.node_id
        self.notify_observers(self[key], 'del')
        NodeDict.pop(self, key)
        
        
    def on_window_close(self, window):
        self.root_node.stream_manager.write(f'WaveSyn:\n{window.node_path} is closed, and its ID becomes defunct for scripting system hereafter.\n', 'TIP')
        self.pop(id(window))
