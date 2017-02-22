# -*- coding: utf-8 -*-
"""
Created on Sun Jan 10 16:55:14 2016

@author: Feng-cong Li
"""
from __future__ import print_function, division

from importlib import import_module

from wavesynlib.languagecenter.wavesynscript import (
    ModelNode, NodeDict, Scripting)
from wavesynlib.languagecenter.utils import eval_format
from wavesynlib.languagecenter.designpatterns import Observable



class BaseWindowNode(ModelNode):
    pass



class WindowDict(NodeDict, Observable):
    def __init__(self, node_name=''):
        NodeDict.__init__(self, node_name=node_name)
        Observable.__init__(self)
                
    def __setitem__(self, key, val):
        if not isinstance(val, BaseWindowNode):
            raise TypeError(eval_format("{self.node_path} only accepts instance of BaseWindowNode's subclasses."))
        if key != id(val):
            raise ValueError('The key should be identical to the ID of the window.')
        NodeDict.__setitem__(self, key, val)
        self.notify_observers(val, 'new')
        
    @Scripting.printable
    def create(self, module_name, class_name):
        mod = import_module(module_name)
        return self.add(node=getattr(mod, class_name)())        
        
    def add(self, node):
        self[id(node)] = node
        return id(node)
        
    def pop(self, key):
        self.notify_observers(self[key], 'del')
        NodeDict.pop(self, key)
        
    def on_window_close(self, window):
        self.root_node.print_tip(
            eval_format(
                '{window.node_path} is closed, and its ID becomes defunct for scripting system hereafter.'))
        self.pop(id(window))
