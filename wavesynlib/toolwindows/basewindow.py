# -*- coding: utf-8 -*-
"""
Created on Sun Jan 10 16:55:14 2016

@author: Feng-cong Li
"""

from six.moves.tkinter import Toplevel, Frame, IntVar
from six.moves.tkinter_ttk import Notebook, Label, Button, Checkbutton

from wavesynlib.languagecenter.wavesynscript import (
    ModelNode, NodeDict, Scripting, code_printer)
from wavesynlib.languagecenter.utils import eval_format, MethodDelegator

from wavesynlib.guicomponents.tk import Group


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
        if isinstance(self.parent_node, WindowDict):
            return eval_format('{self.parent_node.node_path}[{id(self)}]')
        else:
            return ModelNode.node_path
            
    @property
    def tk_object(self):
        return self.__tk_object
        
        
class WindowComponent(object):
    @property        
    def window_node(self):
        node = self
        while True:
            node = node.parent_node
            if isinstance(node, TkWindowNode):
                return node         
        
        
class WindowManager(ModelNode, WindowComponent):
    def __init__(self):
        ModelNode.__init__(self)
        
    def _make_widgets(self):
        tool_tabs = self.window_node._tool_tabs        
        tab = Frame(tool_tabs)
        
        # Start Info Group {
        info_group = Group(tab)
        info_group.pack(side='left', fill='y')
        info_group.name = 'Info'
        Label(info_group, text=eval_format('ID: {id(self.window_node)}')).pack()
        Button(info_group, text='Copy ID', 
               command=self._on_copy_id_click).pack()
        # } End Info Group 
               
        # Start Attributes Group {
        attr_group = Group(tab)
        attr_group.pack(side='left', fill='y')
        attr_group.name = 'Attributes'
        
        self.__topmost = topmost = IntVar(0)
        Checkbutton(attr_group, text='Topmost', 
                    variable=topmost, 
                    command=self._on_topmost_click).pack()
        # } End Attributes Group
        
        tool_tabs.add(tab, text='Window Manager')
        
    def _on_copy_id_click(self):
        with code_printer:
            self.copy_id()
            
    def _on_topmost_click(self):
        with code_printer:
            topmost = True if self.__topmost.get() else False
            self.set_topmost(topmost)

    @Scripting.printable        
    def copy_id(self):
        self.root_node.clipboard.write(id(self.window_node))

    @Scripting.printable
    def set_topmost(self, b):
        self.window_node.tk_object.wm_attributes('-topmost', b)                

 
class TkToolWindow(TkWindowNode):
    '''Tk Window Node with a tabbed toolbar.'''
    def __init__(self, *args, **kwargs):
        super(TkToolWindow, self).__init__(*args, **kwargs)
        tool_tabs = Notebook(self.tk_object)
        tool_tabs.pack(fill='x')
        with self.attribute_lock:
            self._tool_tabs = tool_tabs
            self.window_manager = WindowManager()
            
    def _make_window_manager_tab(self):
        self.window_manager._make_widgets()
        
            

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
         
        