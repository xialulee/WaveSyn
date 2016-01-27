# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 16:47:12 2016

@author: Feng-cong Li
"""

import six.moves.tkinter as tk
import six.moves.tkinter_ttk as ttk

import thread

from wavesynlib.interfaces.timer.tk import TkTimer
from wavesynlib.languagecenter.designpatterns import SimpleObserver

class Dialog(object):
    def __init__(self):
        self.__win = win = tk.Toplevel()
        win.protocol("WM_DELETE_WINDOW", self._on_close)
        progress = tk.IntVar()
        self.__progress = 0
        self.__lock = thread.allocate_lock()        
        ttk.Progressbar(win, orient='horizontal', variable=progress, maximum=100).pack()
        
        self.__timer = timer = TkTimer(widget=win, interval=50)
        
        @SimpleObserver
        def on_timer():
            progress.set(self.progress)
            
        timer.add_observer(on_timer)
        timer.active = True        
        
    def close(self):
        self._on_close()
        
    @property
    def progress(self):
        with self.__lock:
            return self.__progress
            
    @progress.setter
    def progress(self, value):
        with self.__lock:
            self.__progress = value
            
    def _on_close(self):
        self.__timer.active = False
        self.__win.destroy()
            