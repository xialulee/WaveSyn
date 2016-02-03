# -*- coding: utf-8 -*-
"""
Created on Wed Feb 03 16:00:18 2016

@author: Feng-cong Li
"""
from __future__ import print_function, division, unicode_literals

import six.moves.tkinter as tk
import os
import thread
import threading
import six.moves.queue
import hashlib

from wavesynlib.guicomponents.tk import ScrolledTree
from wavesynlib.languagecenter.designpatterns import Observable, SimpleObserver
from wavesynlib.languagecenter.wavesynscript import Scripting, ModelNode
from wavesynlib.interfaces.timer.tk import TkTimer


class ReplicaFinder(Observable, ModelNode):
    def __init__(self, timer=None):
        Observable.__init__(self)
        ModelNode.__init__(self)
        self.__block_size = 64 * 2**10
        self.__stop_event = threading.Event()
        self.__result_lock = thread.allocate_lock()
        self.__result = {}
        self.__queue = six.moves.queue.Queue()
        
        self.__timer = timer
        if timer is None:
            self.__timer = TkTimer(interval=100, active=False)
        self.__timer.add_observer(SimpleObserver(self._on_timer))
            
    def _on_timer(self):
        while True:
            try:
                md5, path = self.__queue.get_nowait()
                self.notify_observers(md5, path)
                print(md5, path)
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
        self.__timer.active = True
        thread.start_new_thread(self._thread_finder, (path,))
    
    def _thread_finder(self, path):
        flag = False
        for root, dirs, files in os.walk(path):
            for filename in files:
                if self.__stop_event.is_set():
                    self.__stop_event.clear()
                    flag = True
                    break
                full_path = os.path.join(root, filename)
                md5 = self._calc_md5(full_path)
                #print(full_path)
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
    
    @Scripting.printable
    def stop(self):
        self.__stop_event.set()
        self.__timer.active = False
        while True:
            # Clear the queue
            try:            
                self.__queue.get_nowait()
            except six.moves.queue.Empty:
                break


if __name__ == '__main__':
    window  = tk.Tk()
    tree_container = ScrolledTree(window)
    tree = tree_container.tree
    tree['columns'] = ['path', 'size']
    tree.heading('path', text='Path')
    tree.heading('size', text='Size')
    root = tree_container.insert('', 'end', text='root')
    node = tree_container.insert(root, 'end', text='node')
    
    finder = ReplicaFinder()
    finder.thread_run('C:/lab')    
    
    window.mainloop()
  