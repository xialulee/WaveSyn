# -*- coding: utf-8 -*-
"""
Created on Wed Feb 03 16:00:18 2016

@author: Feng-cong Li
"""
from __future__ import print_function, division, unicode_literals

import six.moves.tkinter as tk
import six.moves.tkinter_ttk as ttk
import six.moves.tkinter_tkfiledialog as tkfiledialog
import os
import thread
import threading
import six.moves.queue
import hashlib

from wavesynlib.guicomponents.tk import ScrolledTree, Group, DirIndicator
from wavesynlib.toolwindows.basewindow import TkToolWindow
from wavesynlib.languagecenter.designpatterns import Observable, SimpleObserver
from wavesynlib.languagecenter.wavesynscript import Scripting, ModelNode, code_printer
from wavesynlib.languagecenter.utils import get_caller_dir
from wavesynlib.interfaces.timer.tk import TkTimer


def md5_to_string(md5):
    return ''.join(['{:x}'.format(ord(c)) for c in md5])

class ReplicaFinder(Observable, ModelNode):
    def __init__(self, timer=None):
        Observable.__init__(self)
        ModelNode.__init__(self)
        self.__block_size = 64 * 2**10
        self.__stop_event = threading.Event()
        self.__dead_event = threading.Event()
        self.__is_alive = False
        self.__result_lock = thread.allocate_lock()
        self.__result = {}
        self.__queue = six.moves.queue.Queue()
        
        self.__timer = timer
        if timer is None:
            self.__timer = TkTimer(interval=200, active=False)
        self.__timer.add_observer(SimpleObserver(self._on_timer))
            
    def _on_timer(self):
        while True:
            if self.__dead_event.is_set():
                self.notify_observers(None, None, stop=True)
                self.__dead_event.clear()
                self.__is_alive = False
                break

            try:
                md5, path = self.__queue.get_nowait()
                self.notify_observers(md5, path, stop=not self.__is_alive)
            except six.moves.queue.Empty:
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
                                self.__queue.put((md5, self.__result[md5][0]))
                            self.__result[md5].append(full_path)
                            self.__queue.put((md5, full_path))
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
            except six.moves.queue.Empty:
                break


class ReplicaTreeview(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.__md5_dict = {}
        self._make_widgets()
        
    def _make_widgets(self):
        tree_container = ScrolledTree(self)
        tree_container.pack(expand='yes', fill='both')
        self.__tree = tree = tree_container.tree
        tree['columns'] = ['path', 'size']
        tree.heading('path', text='Path')
        tree.heading('size', text='Size')
        
    def update(self, md5, path, stop):
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
            

class ReplicaFinderWindow(TkToolWindow):
    window_name = 'WaveSyn-ReplicaFinder'    
    
    def __init__(self):
        TkToolWindow.__init__(self)
        
        finder_tab = tk.Frame(self._tool_tabs)
        self._tool_tabs.add(finder_tab, text='Finder')
        
        # Start select group {
        select_group = Group(finder_tab)
        select_group.pack(side='left', fill='y')
        select_group.name = 'Finder'
        self.__start_button = start_button = ttk.Button(select_group, 
                   text='Start', 
                   command=self._on_start_click)
        start_button.pack(fill='y')
        ttk.Button(select_group, text='Stop',
                   command=self._on_stop_click).pack(fill='y')
        # } End
                   
        self._make_window_manager_tab()
        
        with self.attribute_lock:
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
        
    def update(self, md5, path, stop, laststate=[None]):
        if stop != laststate[0]:
            state = 'normal' if stop else 'disabled'
            laststate[0] = stop
            self.__start_button['state'] = state
                               
    def _on_start_click(self):
        self.__treeview.clear()
        self.__start_button['state'] = 'disabled'
        with code_printer:
            self.replica_finder.thread_run(self.__dir_indicator.directory)
        
    def _on_stop_click(self):
        with code_printer:
            self.replica_finder.stop()


if __name__ == '__main__':
    window  = tk.Tk()
#    tree_container = ScrolledTree(window)
#    tree = tree_container.tree
#    tree['columns'] = ['path', 'size']
#    tree.heading('path', text='Path')
#    tree.heading('size', text='Size')
#    root = tree_container.insert('', 'end', text='root')
#    node = tree_container.insert(root, 'end', text='node')
#    
#    finder = ReplicaFinder()
#    finder.thread_run('C:/lab')   
#    treeview = ReplicaTreeview(window)
#    treeview.pack(expand='yes', fill='both')
#    finder = ReplicaFinder()
#    finder.add_observer(treeview)
#    finder.thread_run('c:/lab')
    
    window.mainloop()
  