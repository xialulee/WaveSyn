# -*- coding: utf-8 -*-
"""
Created on Sun Jan 10 16:55:14 2016

@author: Feng-cong Li
"""

from six.moves.tkinter import Toplevel
from six.moves.tkinter_ttk import Notebook

from wavesynlib.languagecenter.wavesynscript import (
    ModelNode, NodeDict, Scripting, code_printer)
from wavesynlib.languagecenter.utils import eval_format, MethodDelegator


class BaseWindowNode(ModelNode):
    pass

# To Do: Window Manager. 
#   Window ID Copy
#   Window Foremost
#   Window Info Displayer
class TkWindowNode(BaseWindowNode):
    '''The base class of all the Window Node in the WaveSyn Object Model.
Properties:
    tk_object: The underlying Tk Toplevel object;
    node_path: The path of this node on the WaveSyn Object Model Tree.
Properties inherited from ModelNode:
    root_node: The root node of the WaveSyn Object Model Tree.
'''
    windowName = ''

    _xmlrpcexport_  = ['close']    
    
    def __init__(self, *args, **kwargs):
        super(TkWindowNode, self).__init__(*args, **kwargs)
        self.__tk_object = Toplevel()
        self.__tk_object.title(eval_format('{self.windowName} id={id(self)}'))        
        self.__tk_object.protocol('WM_DELETE_WINDOW', self.on_close)
                
    method_name_map   = {
        'update':'update', 
        'set_window_attributes':'wm_attributes'
    }
    
    for method_name in method_name_map:
        locals()[method_name] = MethodDelegator('tk_object', 
                                                method_name_map[method_name])        
        
    @Scripting.printable
    def close(self):
        Scripting.root_node.on_window_quit(self)
        # For Toplevel objects, use destroy rather than quit.
        self.__tk_object.destroy() 
        
    def on_close(self):
        with code_printer:
            self.close()
        
    @property
    def node_path(self):
        if isinstance(self.parentNode, WindowDict):
            return eval_format('{self.parentNode.node_path}[{id(self)}]')
        else:
            return ModelNode.node_path
            
    @property
    def tk_object(self):
        return self.__tk_object

 
class TkToolWindow(TkWindowNode):
    '''Tk Window Node with a tabbed toolbar.'''
    def __init__(self, *args, **kwargs):
        super(TkToolWindow, self).__init__(*args, **kwargs)
        tool_tabs = Notebook(self.tk_object)
        tool_tabs.pack(fill='x')
        with self.attribute_lock:
            self.tool_tabs = tool_tabs
            

class WindowDict(NodeDict):
    def __init__(self, node_name=''):
        super(WindowDict, self).__init__(node_name=node_name)
                
    def __setitem__(self, key, val):
        if not isinstance(val, BaseWindowNode):
            raise TypeError, eval_format("{self.node_path} only accepts instance of BaseWindowNode's subclasses.")
        if key != id(val):
            raise ValueError, 'The key should be identical to the ID of the window.'
        NodeDict.__setitem__(self, key, val)
        
    def add(self, node):
        self[id(node)] = node
        return id(node)
         
        
class WindowComponent(object):
    @property        
    def top_window(self):
        if hasattr(self, '_top_window'):
            return self._top_window
        else:
            node    = self
            while True:
                node    = node.parentNode
                if isinstance(node, TkWindowNode):
                    self._top_window    = node
                    return node 