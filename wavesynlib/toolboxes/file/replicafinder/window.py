# -*- coding: utf-8 -*-
"""
Created on Wed Feb 03 16:00:18 2016

@author: Feng-cong Li
"""
import hy
import tkinter as tk

import os
import _thread as thread
import threading
import queue
import hashlib

from pathlib import Path

from quantities import second

from wavesynlib.widgets.tk.scrolledtree import ScrolledTree
from wavesynlib.widgets.tk.desctotk import json_to_tk
from wavesynlib.widgets.tk.dirindicator import DirIndicator
from wavesynlib.widgets.tk.tkbasewindow import TkToolWindow
from wavesynlib.languagecenter.datatypes import Event
from wavesynlib.languagecenter.designpatterns import Observable, SimpleObserver
from wavesynlib.languagecenter.wavesynscript import Scripting, WaveSynScriptAPI, ModelNode, code_printer
from wavesynlib.interfaces.timer.tk import TkTimer

from .widgets import (
    finder_grp, status_frm)


_image_dir = Path(__file__).parent / 'images'



def md5_to_string(md5):
    return ''.join([f'{c:x}' for c in md5])



class ReplicaFinder(Observable, ModelNode):
    def __init__(self, timer=None):
        super().__init__()
        self.__block_size = 64 * 2**10
        self.__stop_event = threading.Event()
        self.__dead_event = threading.Event()
        self.__is_alive = False
        self.__result_lock = thread.allocate_lock()
        self.__result = {}
        self.__queue = queue.Queue()
        
        self.__timer = timer
        if timer is None:
            self.__timer = TkTimer(interval=0.2*second, active=False)
        self.__timer.add_observer(self._on_timer)
        
            
    def _on_timer(self, event):
        while True:
            if self.__dead_event.is_set():
                self.notify_observers(Event(
                    name = "stop_searching",
                    kwargs = {
                        "md5":         None,
                        "path":        None,
                        "current_dir": None,
                        "stop":        True }))
                self.__dead_event.clear()
                self.__is_alive = False
                break

            try:
                md5, path, current_dir = self.__queue.get_nowait()
                self.notify_observers(Event(
                    name = "find",
                    kwargs = {
                        "md5": md5,
                        "path": path,
                        "current_dir": current_dir,
                        "stop": not self.__is_alive }))
            except queue.Empty:
                break
            
        
    def _calc_md5(self, filename):
        with open(filename, 'rb') as f:
            m = hashlib.md5()
            while True:
                data = f.read(self.__block_size)
                if not data:
                    break
                m.update(data)
        return m.digest()
    
        
    @WaveSynScriptAPI
    def set_block_size(self, block_size):
        self.__block_size = block_size
        
        
    # To do: Make a thread-safe WaveSynAPI
    @WaveSynScriptAPI
    def thread_run(self, path):
        self.__result = {}
        self.__timer.active = True
        self.__is_alive = True
        self.root_node.thread_manager.new_thread_do(lambda: self._thread_finder(path))
        
    
    def _thread_finder(self, path):
        try:
            flag = False
            for root, dirs, files in os.walk(path):
                self.__queue.put((None, None, root))
                if self.__stop_event.is_set():
                    self.__stop_event.clear()
                    break                
                for filename in files:
                    if self.__stop_event.is_set():
                        self.__stop_event.clear()
                        flag = True
                        break
                    full_path = os.path.join(root, filename)
                    md5 = self._calc_md5(full_path)
                    
                    with self.__result_lock:
                        if md5 in self.__result:
                            if len(self.__result[md5]) == 1:
                                self.__queue.put((md5, self.__result[md5][0], None))
                            self.__result[md5].append(full_path)
                            self.__queue.put((md5, full_path, None))
                        else:
                            self.__result[md5] = [full_path]
                if flag:
                    break
        finally:
            # Indicating that this thread is dead.
            self.__dead_event.set()
            
    
    @WaveSynScriptAPI
    def stop(self):
        self.__stop_event.set()
        # self.__timer.active = False
        while True:
            # Clear the queue
            try:            
                self.__queue.get_nowait()
            except queue.Empty:
                break
            


class ReplicaTreeview(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__md5_dict = {}
        self._make_widgets()
        
        
    def _make_widgets(self):
        tree_container = ScrolledTree(self)
        tree_container.pack(expand='yes', fill='both')
        self.__tree = tree = tree_container.tree
        tree['columns'] = ['path', 'size']
        tree.heading('path', text='Path')
        tree.heading('size', text='Size')
        tree_container.on_item_double_click.add_function(self._on_item_doubleclick)
        
        
    def update(self, event):
        kwargs = event.kwargs
        md5         = kwargs["md5"]
        path        = kwargs["path"]
        stop        = kwargs["stop"]
        if md5 is None:
            return
            
        md5_dict = self.__md5_dict

        if md5 not in md5_dict:
            md5_node = self.__tree.insert('', 'end', text=md5_to_string(md5))
            md5_dict[md5] = md5_node
        else:
            md5_node = md5_dict[md5]
        
        self.__tree.insert(md5_node, 'end', text=os.path.split(path)[-1], 
                           values=(path, str(os.path.getsize(path))))
        
                           
    def clear(self):
        self.__md5_dict = {}
        tree = self.__tree
        for row in tree.get_children():
            tree.delete(row)
            
            
    def _on_item_doubleclick(self, item_id, item_properties):
        try:
            path = item_properties['values'][0]
        except IndexError:
            return
        with code_printer():
            Scripting.root_node.interfaces.os.win_open(path)
            
            

class ReplicaFinderWindow(TkToolWindow):
    window_name = 'WaveSyn-ReplicaFinder'    
    
    
    def __init__(self):
        super().__init__()
                
        finder_tab = tk.Frame(self._tool_tabs)
        self._tool_tabs.add(finder_tab, text='Finder')
        
        widgets_desc = [finder_grp]
        widgets = json_to_tk(finder_tab, widgets_desc)
        
        widgets['start_btn']['command'] = self._on_start_click
        widgets['stop_btn']['command'] = self._on_stop_click
        self.__start_button = widgets['start_btn']
                   
        self._make_window_manager_tab()

        self.replica_finder = ReplicaFinder()
            
        self.__dir_indicator = dir_indicator = DirIndicator(self.tk_object)
        dir_indicator.pack(fill='x')
        cwd = os.getcwd()
        if os.path.altsep is not None: # Windows OS
            cwd = cwd.replace(os.path.altsep, os.path.sep)
        dir_indicator.change_dir(cwd)        
        
        self.__treeview = treeview = ReplicaTreeview(self.tk_object)
        treeview.pack(expand='yes', fill='both')
        self.replica_finder.add_observer(treeview)
        self.replica_finder.add_observer(self)  
        
        widgets_desc = [status_frm]
        widgets = json_to_tk(self.tk_object, widgets_desc)
        self.__busy_light = widgets['light_lbl']
        self.__current_dir_label = widgets['current_dir_lbl']
              
        
    def update(self, event, laststate=[None]):
        kwargs = event.kwargs
        md5 = kwargs["md5"]
        path = kwargs["path"]
        current_dir = kwargs["current_dir"]
        stop = kwargs["stop"]
        if not stop: 
            if current_dir:
                self.__current_dir_label['text'] = current_dir
        else:
            self.__current_dir_label['text'] = ''
            
        if stop != laststate[0]:
            laststate[0] = stop            
            state = 'normal' if stop else 'disabled'
            self.__start_button['state'] = state
            busy = False if stop else True
            self.__busy_light.busy = busy

                               
    def _on_start_click(self):
        self.__treeview.clear()
        self.__start_button['state'] = 'disabled'
        self.__busy_light.busy = True
        with code_printer():
            self.replica_finder.thread_run(self.__dir_indicator.directory)
            
        
    def _on_stop_click(self):
        with code_printer():
            self.replica_finder.stop()



if __name__ == '__main__':
    window  = tk.Tk()
    window.mainloop()
  