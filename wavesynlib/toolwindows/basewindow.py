# -*- coding: utf-8 -*-
"""
Created on Sun Jan 10 16:55:14 2016

@author: Feng-cong Li
"""
from __future__ import print_function, division

from six.moves.tkinter import Toplevel, Frame, IntVar
from six.moves.tkinter_ttk import Notebook, Label, Button, Checkbutton, Scale

from PIL import ImageTk
from wavesynlib.application import get_gui_image_path

from wavesynlib.languagecenter.wavesynscript import (
    ModelNode, NodeDict, Scripting, code_printer)
from wavesynlib.languagecenter.utils import auto_subs, eval_format, MethodDelegator
from wavesynlib.languagecenter.designpatterns import Observable

from wavesynlib.guicomponents.tk import Group, json_to_tk


class BaseWindowNode(ModelNode):
    pass


class TkWindowNode(BaseWindowNode):
    '''The base class of all the Window Node in the WaveSyn Object Model.
Properties:
    tk_object: The underlying Tk Toplevel object;
    node_path: The path of this node on the WaveSyn Object Model Tree.
Properties inherited from ModelNode:
    root_node: The root node of the WaveSyn Object Model Tree.
'''
    window_name = ''

    _xmlrpcexport_  = ['close']    
    
    def __init__(self, *args, **kwargs):
        super(TkWindowNode, self).__init__(*args, **kwargs)
        self.__tk_object = Toplevel()
        self.__tk_object.title(eval_format('{self.window_name} id={id(self)}'))        
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
            return ModelNode.node_path.__get__(self)
            
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
        self.__gui_images = []
        
    def _make_widgets(self):
        tool_tabs = self.window_node._tool_tabs        
        
        self.__topmost = topmost = IntVar(0)
        
        copy_id_icon = ImageTk.PhotoImage(file=get_gui_image_path('WindowManager_CopyID.png'))
        self.__gui_images.append(copy_id_icon)
        copy_path_icon = ImageTk.PhotoImage(file=get_gui_image_path('WindowManager_CopyPath.png'))
        self.__gui_images.append(copy_path_icon)
        
        def on_scale(val):
            self.set_transparency(val)        
            
        widgets_desc = [
{"class":"Group", "pack":{"side":"left", "fill":"y"}, "setattr":{"name":"Info"}, "children":[
    {"class":"Label", "config":{"text":eval_format("ID: {id(self.window_node)}")}},
    {"class":"Button", "config":{"text":"Copy ID  ", "image":copy_id_icon, "compound":"left", "command":self._on_copy_id_click}},
    {"class":"Button", "config":{"text":"Copy Path", "image":copy_path_icon, "compound":"left", "command":self._on_copy_path_click}}]
},

{"class":"Group", "pack":{"side":"left", "fill":"y"}, "setattr":{"name":"Attributes"}, "children":[
    {"class":"Checkbutton", "config":{"text":"Topmost", "variable":topmost, "command":self._on_topmost_click}},
    {"class":"Scale", "config":{"from_":0.2, "to":1.0, "orient":"horizontal", "value":1.0, "command":on_scale}},
    {"class":"Label", "config":{"text":"Transparency"}}]
}
]

        tab = Frame(tool_tabs)
        json_to_tk(tab, widgets_desc)        
        tool_tabs.add(tab, text='Window Manager')
        
    def _on_copy_id_click(self):
        with code_printer:
            self.copy_window_id()
            
    def _on_copy_path_click(self):
        with code_printer:
            self.copy_window_path()
            
    def _on_topmost_click(self):
        with code_printer:
            topmost = True if self.__topmost.get() else False
            self.set_topmost(topmost)

    @Scripting.printable        
    def copy_window_id(self):
        self.root_node.os.clipboard.write(id(self.window_node))
        
    @Scripting.printable
    def copy_window_path(self):
        self.root_node.os.clipboard.write(self.window_node.node_path)

    @Scripting.printable
    def set_topmost(self, b):
        self.window_node.tk_object.wm_attributes('-topmost', b)

    @Scripting.printable
    def set_transparency(self, transparency):
        self.window_node.tk_object.wm_attributes('-alpha', transparency)                

 
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
        
            

class WindowDict(NodeDict, Observable):
    def __init__(self, node_name=''):
        NodeDict.__init__(self, node_name=node_name)
        Observable.__init__(self)
                
    def __setitem__(self, key, val):
        if not isinstance(val, BaseWindowNode):
            raise TypeError, eval_format("{self.node_path} only accepts instance of BaseWindowNode's subclasses.")
        if key != id(val):
            raise ValueError, 'The key should be identical to the ID of the window.'
        NodeDict.__setitem__(self, key, val)
        self.notify_observers(val, 'new')
        
    def add(self, node):
        self[id(node)] = node
        return id(node)
        
    def pop(self, key):
        self.notify_observers(self[key], 'del')
        NodeDict.pop(self, key)
         
        
