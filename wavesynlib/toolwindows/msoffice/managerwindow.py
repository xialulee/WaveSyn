# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 15:33:03 2017

@author: Feng-cong Li
"""
import os
from pathlib import Path
from comtypes import COMError

import tkinter as tk
from tkinter import ttk

import hy
from wavesynlib.widgets.scrolledtree import ScrolledTree
from wavesynlib.widgets.tk import json_to_tk
from wavesynlib.widgets.group import Group
from wavesynlib.toolwindows.tkbasewindow import TkToolWindow
from wavesynlib.languagecenter.wavesynscript import Scripting, WaveSynScriptAPI, code_printer
from wavesynlib.languagecenter.designpatterns import SimpleObserver



# The following code generates the bytecode file of the 
# widgets.hy which is written in Hy.
# If we import a module written in hy directly in wavesyn,
# it will fail, and I cannot figure out why. 
import hy
try:
    from wavesynlib.toolwindows.msoffice.widgets import (
            connect_grp, window_grp, utils_grp)
except hy.errors.HyCompileError:
# After the bytecode file generated, we can import the module written by hy.    
    widgets_path = Path(__file__).parent / 'widgets.hy'
    os.system(f'hyc {widgets_path}')    
    from wavesynlib.toolwindows.msoffice.widgets import (
            connect_grp, window_grp, utils_grp)



class AppTreeview(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._make_widgets()
        
        
    def _make_widgets(self):
        tree_container = ScrolledTree(self)
        tree_container.pack(expand='yes', fill='both')
        self.__tree = tree = tree_container.tree
        tree['columns'] = ['app', 'id']
        tree.heading('app', text='App')
        tree.heading('id', text='ID')
        self._tree = tree
        
        
    def update(self, app_dict):
        self.clear()
        for id_ in app_dict:
            obj = app_dict[id_]
            node = self.__tree.insert('', 'end', text=obj.caption, values=(obj.name, id_), open=True)
            if obj.name.lower() == 'word':
                for window in obj.windows:
                    self.__tree.insert(node, 'end', text=window.Caption, values=('Word', ''))
            
            
    def clear(self):
        tree = self.__tree
        for row in tree.get_children():
            tree.delete(row)
            
            
            
class OfficeController(TkToolWindow):
    window_name = 'WaveSyn-MSOfficeController'
    
    
    def __init__(self):
        super().__init__()
        
        
    def on_connect(self):
        self._gui_images = []
        tool_tabs = self._tool_tabs
        
        widgets_desc = [connect_grp, window_grp, utils_grp]
      
        tab = tk.Frame(tool_tabs)
        widgets = json_to_tk(tab, widgets_desc)
        
        widgets['get_active_btn']['command'] = self.__on_get_active
        widgets['create_btn']['command'] = self.__on_create
        
        widgets['foreground_btn']['command'] = self.__on_foreground
        widgets['copypath_btn']['command'] = self.__on_copy_path

        self.__utils_group = utils_group = widgets['utils_grp']
        # Utils panel if no item is selected.
        self.__null_utils_frame = null_utils_frame = tk.Frame(utils_group)
        null_utils_frame.pack(fill='both')
        tk.Label(null_utils_frame, text='No Utils Available').pack(fill='both')
        self.__current_utils_frame = null_utils_frame
        # Utils panel if a Word instance is selected.
        self.__word_utils_frame = word_utils_frame = tk.Frame(utils_group)
        ttk.Button(word_utils_frame, text='Insert PSD', command=self.__on_insert_psd).pack(fill='x')
        ttk.Button(word_utils_frame, text='Update PSD', command=self.__on_update_psd).pack(fill='x')
        # Utils panel if an Excel instance is selected.
        self.__excel_utils_frame = excel_utils_frame = tk.Frame(utils_group)
        tk.Label(excel_utils_frame, text='Excel Utils').pack(fill='both')
        
        tool_tabs.add(tab, text='Office')
        
        self._make_window_manager_tab()
        self.__treeview = treeview = AppTreeview(self.tk_object)
        treeview.pack(expand='yes', fill='both')
        treeview._tree.bind('<<TreeviewSelect>>', self.__on_select)
        app_dict = self.root_node.interfaces.msoffice
        treeview.update(app_dict)        
                
        @SimpleObserver
        def app_observer(*args, **kwargs):
            # At this moment it seems that we cannot access the message loop,
            # since if we use after method of tk, it will block.
            import time
            @self.root_node.thread_manager.new_thread_do
            def wait(treeview=treeview):
                # Wait for 2.5 sec. If we call treeview.update immediately, 
                # it will block (maybe because the update method will access the app model tree).
                time.sleep(2.5)
                @self.root_node.thread_manager.main_thread_do(block=False)
                def update_tree():
                    event_desc = ' '.join((
                        kwargs['app'], 
                        kwargs['source'], 
                        kwargs['event']))
                    if event_desc in {
                            'Word Application NewDocument',
                            'Word Application DocumentOpen',
                            'Word Application Quit',
                            'Word Document Close'}:
                        treeview.update(app_dict)
            
        self.__app_observer = app_observer
            
        app_dict.add_observer(app_observer)
        
        
    def __get_selected(self):
        tree = self.__treeview._tree
        iid = tree.selection()[0]
        cur = tree.item(iid)
        app_name = cur['values'][0].lower()
        id_ = cur['values'][1]
        txt = cur['text']
        if app_name == 'excel':
            return id_, app_name, txt, True
        elif app_name == 'word':
            if id_:
                return id_, app_name, txt, True
            else:
                piid = tree.parent(iid)                
                app_id = tree.item(piid)['values'][1]
                return app_id, app_name, txt, False
        else:
            raise ValueError
        
        
    def __connect_app(self, app_name=None, get_active=True):
        if app_name is None:
            app_name = self.root_node.lang_center.wavesynscript.constants.ASK_LIST_ITEM

        msoffice = self.root_node.interfaces.msoffice
        
        with code_printer():
            if get_active:
                msoffice.get_active(app_name=app_name)
            else:
                msoffice.create(app_name=app_name)
        self.__treeview.update(msoffice)        
        
        
    def __on_get_active(self, app_name=None):
        self.__connect_app(app_name)
        
        
    def __on_create(self, app_name=None):
        self.__connect_app(app_name, get_active=False)
        
        
    def __on_foreground(self):
        office = self.root_node.interfaces.msoffice                
        id_, app_name, txt, is_parent = self.__get_selected()
        kwargs = {}
        if app_name == 'word' and not is_parent:
            kwargs['index'] = txt
        with code_printer(print_=True):
            try:
                office[id_].set_foreground(**kwargs)
            except COMError as err:
                tk.messagebox.showerror(
                    title = 'Office Error',
                    message = 
                        '\n'.join([str(item) for item in err.details]))
                
                
    def __on_select(self, event):
        tree = self.__treeview._tree
        cur = tree.item(tree.selection())
        app_name = cur['values'][0].lower()
        if app_name == 'word':
            if self.__current_utils_frame is not self.__word_utils_frame:
                self.__current_utils_frame.pack_forget()
                self.__word_utils_frame.pack(fill='both')
                self.__current_utils_frame = self.__word_utils_frame
        elif app_name == 'excel':
            if self.__current_utils_frame is not self.__excel_utils_frame:
                self.__current_utils_frame.pack_forget()
                self.__excel_utils_frame.pack(fill='both')
                self.__current_utils_frame = self.__excel_utils_frame
    
    
    def __on_insert_psd(self):
        office = self.root_node.interfaces.msoffice
        kwargs = {'filename':self.root_node.lang_center.wavesynscript.constants.ASK_OPEN_FILENAME}
        id_, app_name, txt, is_parent = self.__get_selected()
        if not is_parent:
            kwargs['window'] = txt
        with code_printer():
            office[id_].utils.insert_psd_image(**kwargs)
    
    
    def __on_update_psd(self):
        office = self.root_node.interfaces.msoffice
        id_, app_name, txt, is_parent = self.__get_selected()
        if not is_parent:
            window = txt
        else:
            window = None
        with code_printer():
            office[id_].utils.update_psd_images(window=window)
    
    
    @WaveSynScriptAPI
    def copy_selected_path(self):
        id_, app_name, txt, is_parent = self.__get_selected()
        office = self.root_node.interfaces.msoffice
        path = f'{office.node_path}[{id_}]'
        self.root_node.interfaces.os.clipboard.write(path)        
    
    
    def __on_copy_path(self):
        with code_printer():
            self.copy_selected_path()
            
            
    @WaveSynScriptAPI
    def close(self):
        self.root_node.interfaces.msoffice.delete_observer(self.__app_observer)
        super().close()
