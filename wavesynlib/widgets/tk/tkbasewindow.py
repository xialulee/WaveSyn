# -*- coding: utf-8 -*-
"""
Created on Wed Feb 22 13:50:57 2017

@author: Feng-cong Li
"""
from importlib import import_module

from tkinter import Toplevel, Frame, IntVar
from tkinter.ttk import Notebook, Label, Button, Checkbutton, Scale


from PIL import ImageTk

from wavesynlib.languagecenter.wavesynscript import (
    ModelNode, NodeDict, Scripting, WaveSynScriptAPI, code_printer)
from wavesynlib.languagecenter.utils import auto_subs, MethodDelegator
from wavesynlib.languagecenter.designpatterns import Observable
from wavesynlib.interfaces.timer.tk import TkTimer
from wavesynlib.widgets.tk.group import Group
from wavesynlib.widgets.tk.desctotk import json_to_tk
from wavesynlib.widgets.basewindow import BaseWindowNode


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
        super().__init__(*args, **kwargs)
        self.__tk_object = Toplevel()
        self.__tk_object.title(f'{self.window_name} id={id(self)}')
        self.__tk_object.protocol('WM_DELETE_WINDOW', self.on_close)
    
            
    method_name_map   = {
        'update':'update', 
        'set_window_attributes':'wm_attributes'
    }
    
    for method_name in method_name_map:
        locals()[method_name] = MethodDelegator('tk_object', 
                                                method_name_map[method_name])


    def _close_callback(self):
        pass        

       
    @WaveSynScriptAPI
    def close(self):
        #Scripting.root_node.on_window_quit(self)
        if hasattr(self.parent_node, 'on_window_close'):
            self.parent_node.on_window_close(self)
        # For Toplevel objects, use destroy rather than quit.
        if not self._close_callback():
            self.__tk_object.destroy() 
        
        
    def on_close(self):
        with code_printer():
            self.close()
        
            
    @property
    def tk_object(self):
        return self.__tk_object
    
        
    def create_timer(self, interval=100, active=False):
        return TkTimer(self.__tk_object, interval, active)
        

        
class WindowComponent:
    @property        
    def window_node(self):
        node = self
        while True:
            node = node.parent_node
            if isinstance(node, TkWindowNode):
                return node         
        

        
class WindowManager(ModelNode, WindowComponent):
    def __init__(self):
        super().__init__()
        self.__gui_images = []
        
        
    def _make_widgets(self):
        tool_tabs = self.window_node._tool_tabs        
        
        self.__topmost = topmost = IntVar(value=0)
        
        copy_id_icon = ImageTk.PhotoImage(file=Scripting.root_node.get_gui_image_path('WindowManager_CopyID.png'))
        self.__gui_images.append(copy_id_icon)
        copy_path_icon = ImageTk.PhotoImage(file=Scripting.root_node.get_gui_image_path('WindowManager_CopyPath.png'))
        self.__gui_images.append(copy_path_icon)
        
        def on_scale(val):
            self.set_opacity(val)        
            
        widgets_desc = [
{"class":Group, "pack":{"side":"left", "fill":"y"}, "setattr":{"name":"Info"}, "children":[
    {"class":"Label", "init":{"text":f"ID: {id(self.window_node)}"}},
    {"class":"Button", "init":{"text":"Copy ID  ", "image":copy_id_icon, "compound":"left", "command":self._on_copy_id_click}},
    {"class":"Button", "init":{"text":"Copy Path", "image":copy_path_icon, "compound":"left", "command":self._on_copy_path_click}}]
},

{"class":Group, "pack":{"side":"left", "fill":"y"}, "setattr":{"name":"Attributes"}, "children":[
    {"class":"Checkbutton", "init":{"text":"Topmost", "variable":topmost, "command":self._on_topmost_click}},
    {"class":"Scale", "init":{"from_":0.2, "to":1.0, "orient":"horizontal", "value":1.0, "command":on_scale}},
    {"class":"Label", "init":{"text":"Opacity"}}]
}
]

        tab = Frame(tool_tabs)
        json_to_tk(tab, widgets_desc)        
        tool_tabs.add(tab, text='Window Manager')
        
        
    def _on_copy_id_click(self):
        with code_printer():
            self.copy_window_id()
            
            
    def _on_copy_path_click(self):
        with code_printer():
            self.copy_window_path()
            
            
    def _on_topmost_click(self):
        with code_printer():
            topmost = True if self.__topmost.get() else False
            self.set_topmost(topmost)


    @WaveSynScriptAPI        
    def copy_window_id(self):
        self.root_node.interfaces.os.clipboard.write(id(self.window_node))
        
        
    @WaveSynScriptAPI
    def copy_window_path(self):
        self.root_node.interfaces.os.clipboard.write(self.window_node.node_path)


    @WaveSynScriptAPI
    def set_topmost(self, b):
        self.window_node.tk_object.wm_attributes('-topmost', b)


    @WaveSynScriptAPI
    def set_opacity(self, opacity):
        self.window_node.tk_object.wm_attributes('-alpha', opacity)


 
class TkToolWindow(TkWindowNode):
    '''Tk Window Node with a tabbed toolbar.'''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tool_tabs = Notebook(self.tk_object)
        tool_tabs.pack(fill='x')
        with self.attribute_lock:
            self._tool_tabs = tool_tabs
        self.window_manager = WindowManager()
        
            
    def _make_window_manager_tab(self):
        self.window_manager._make_widgets()
        
            

