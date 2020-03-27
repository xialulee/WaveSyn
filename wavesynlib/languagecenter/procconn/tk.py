# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 23:19:52 2016

@author: Feng-cong Li
"""
from __future__ import print_function, division, unicode_literals

import six
import six.moves.tkinter as tkinter
import six.moves.tkinter_tix as tix

import hy

from wavesynlib.widgets.valuechecker import ValueChecker
from wavesynlib.languagecenter.wavesynscript import Scripting, ModelNode
from wavesynlib.languagecenter.utils import set_attributes
from wavesynlib.languagecenter.designpatterns import Singleton


class NodeDelegate(ModelNode):
    def __init__(self, node_name='', is_root=False):
        ModelNode.__init__(node_name=node_name, is_root=is_root)
    
    def __getattribute__(self, attribute_name):
        new_node = NodeDelegate(node_name=attribute_name, is_root=False)
        with new_node.attribute_lock:
            new_node.parent_node = self
        return new_node
        

@six.add_metaclass(Singleton)
class RootDelegate(NodeDelegate):
    def __init__(self):
        ModelNode.__init__(node_name=Scripting.root_name, is_root=True)
        tk_root = tkinter.Tk()
        tk_root.widthdraw()
        
        with self.attribute_lock:
            set_attributes(self,
                # UI elements
                tk_root = tk_root,
                value_checker = ValueChecker(tk_root),
                balloon = tix.Balloon(tk_root)
                # End UI elements
            )
            
    def print_and_eval(self, expr):
        # Local and Remote objects can be handled the same way.
        # For remote objects, delegate will send command automatically (which means it will not be called in this process).
        pass
    
    
class ProcDictDelegate(NodeDelegate):
    pass