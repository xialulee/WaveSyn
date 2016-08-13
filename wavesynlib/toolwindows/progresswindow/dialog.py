# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 16:47:12 2016

@author: Feng-cong Li
"""

import six.moves.tkinter as tk
import six.moves.tkinter_ttk as ttk

import six.moves._thread as thread

from wavesynlib.interfaces.timer.tk import TkTimer
from wavesynlib.languagecenter.designpatterns import SimpleObserver


class LabeledProgress(tk.Frame, object):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.__label = label = ttk.Label(self)
        label.pack(expand='yes', fill='x')
        self.__progress = progress = tk.IntVar()
        ttk.Progressbar(self, orient='horizontal', 
                        variable=progress, maximum=100,
                        length=400).pack(expand='yes', fill='x')
        
    @property
    def progress(self):
        return self.__progress.get()
        
    @progress.setter
    def progress(self, value):
        self.__progress.set(value)
        
    @property
    def label_text(self):
        return self.__label['text']
        
    @label_text.setter
    def label_text(self, value):
        self.__label['text'] = value


class Dialog(object):
    def __init__(self, text_list, title=''):
        self.__win = win = tk.Toplevel()
        win.protocol("WM_DELETE_WINDOW", self._on_close)
        win.title(title)
        self.__lock = thread.allocate_lock() 
                
        number = len(text_list)        
        self.__progressbars = progressbars = []
        self.__text_list = text_list
        self.__text_changed = False
        self.__progress_list = progress_list = [0]*number                
        for n in range(number):
            progressbar = LabeledProgress(win)
            progressbar.pack(expand='yes', fill='x')
            progressbar.label_text = text_list[n]
            progressbars.append(progressbar)
        
        self.__timer = timer = TkTimer(widget=win, interval=50)
        
        @timer.add_observer
        def on_timer():
            with self.__lock:
                for n in range(number):
                    progressbars[n].progress = progress_list[n]
                if self.__text_changed:
                    self.__text_changed = False
                    for n in range(number):
                        progressbars[n].label_text = self.__text_list[n]
            
        timer.active = True        
        
    def close(self):
        self._on_close()
        
    def set_progress(self, index, progress):
        with self.__lock:
            self.__progress_list[index] = progress
            
    def set_text(self, index, text):
        with self.__lock:
            self.__text_list[index] = text
            self.__text_changed = True
            
    def _on_close(self):
        self.__timer.active = False
        self.__win.destroy()
            
            
def main(argv):
    root = tk.Tk()
    dialog = Dialog(['abcd', 'efgh'])
    dialog.set_progress(index=0, progress=50)
    dialog.set_progress(index=1, progress=80)
    root.mainloop()
    

if __name__ == '__main__':
    main(None)
            