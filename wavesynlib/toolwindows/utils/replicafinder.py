# -*- coding: utf-8 -*-
"""
Created on Wed Feb 03 16:00:18 2016

@author: Feng-cong Li
"""
import tkinter as tk
from tkinter import ttk

import os
import _thread as thread
import threading
import queue
import hashlib

from PIL import ImageTk

from wavesynlib.widgets.tk import ScrolledTree, Group, DirIndicator
from wavesynlib.toolwindows.tkbasewindow import TkToolWindow
from wavesynlib.languagecenter.designpatterns import Observable, SimpleObserver
from wavesynlib.languagecenter.wavesynscript import Scripting, ModelNode, code_printer
from wavesynlib.languagecenter.utils import get_caller_dir
from wavesynlib.interfaces.timer.tk import TkTimer


_image_dir = get_caller_dir()/'images'



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
            self.__timer = TkTimer(interval=200, active=False)
        self.__timer.add_observer(SimpleObserver(self._on_timer))
        
            
    def _on_timer(self):
        while True:
            if self.__dead_event.is_set():
                self.notify_observers(None, None, None, stop=True)
                self.__dead_event.clear()
                self.__is_alive = False
                break

            try:
                md5, path, current_dir = self.__queue.get_nowait()
                self.notify_observers(md5, path, current_dir, stop=not self.__is_alive)
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
    
        
    @Scripting.printable
    def set_block_size(self, block_size):
        self.__block_size = block_size
        
        
    @Scripting.printable
    def thread_run(self, path):
        self.__result = {}
        self.__timer.active = True
        self.__is_alive = True
        thread.start_new_thread(self._thread_finder, (path,))
        
    
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
            
    
    @Scripting.printable
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
        
        
    def update(self, md5, path, current_dir, stop):
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
        
        self._gui_images = []
        
        finder_tab = tk.Frame(self._tool_tabs)
        self._tool_tabs.add(finder_tab, text='Finder')
        
        # Start select group {
        select_group = Group(finder_tab)
        select_group.pack(side='left', fill='y')
        select_group.name = 'Finder'
        
        row = tk.Frame(select_group)
        row.pack()
        
        image_start = ImageTk.PhotoImage(file=_image_dir/'start_button.png')
        self._gui_images.append(image_start)
        self.__start_button = start_button = ttk.Button(row, 
                   image=image_start, 
                   command=self._on_start_click)
        start_button.pack(side='left', fill='y')
        
        image_stop = ImageTk.PhotoImage(file=_image_dir/'stop_button.png')
        self._gui_images.append(image_stop)
        ttk.Button(row, image=image_stop,
                   command=self._on_stop_click).pack(side='left', fill='y')                   
        # } End
                   
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

        # Start Status Bar {
        status_bar = tk.Frame(self.tk_object)
        status_bar.pack(fill='x')
        image_red = ImageTk.PhotoImage(file=_image_dir / 'red_light.png')
        self.__image_red_light = image_red
        image_green = ImageTk.PhotoImage(file=_image_dir / 'green_light.png')
        self.__image_green_light = image_green
        self.__busy_light = ttk.Label(status_bar, image=image_green)
        self.__busy_light.pack(side='right')     
        self.__current_dir_label = ttk.Label(status_bar)
        self.__current_dir_label.pack(side='right')
        # } End   
              
        
    def update(self, md5, path, current_dir, stop, laststate=[None]):
        if not stop: 
            if current_dir is not None:
                self.__current_dir_label['text'] = current_dir
        else:
            self.__current_dir_label['text'] = ''
            
        if stop != laststate[0]:
            laststate[0] = stop            
            state = 'normal' if stop else 'disabled'
            light = self.__image_green_light if stop else self.__image_red_light
            self.__start_button['state'] = state
            self.__busy_light['image'] = light
            
                               
    def _on_start_click(self):
        self.__treeview.clear()
        self.__start_button['state'] = 'disabled'
        self.__busy_light['image'] = self.__image_red_light
        with code_printer():
            self.replica_finder.thread_run(self.__dir_indicator.directory)
            
        
    def _on_stop_click(self):
        with code_printer():
            self.replica_finder.stop()



if __name__ == '__main__':
    window  = tk.Tk()
    window.mainloop()
  