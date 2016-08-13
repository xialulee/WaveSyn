# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26 10:18:01 2016

@author: Feng-cong Li
"""
from __future__ import print_function, division, unicode_literals

import sys

import six.moves.tkinter as tk
import six.moves.tkinter_ttk as ttk
from six.moves import queue

import json
import six.moves._thread as thread

from wavesynlib.interfaces.timer.tk import TkTimer
from wavesynlib.languagecenter.designpatterns import SimpleObserver


message_queue = queue.Queue()


class MainPanel(tk.Frame, object):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        ttk.Label(self, text='''If you start a time consuming loop in the wavesyn's console,
the GUI components will not response anymore. 
If you want to abort this mission, you can click the button below.
''').pack()
        tk.Button(self, text='Abort!', command=self._on_abort, bg='red', fg='white').pack()
        ttk.Label(self).pack()

        
    def _on_abort(self):
        command = {'type':'command', 'command':'interrupt_main_thread', 'args':''}
        command_json = json.dumps(command)
        print(command_json)
        
        
def listener(*args):
    sys.stdin.read()
    message = {'type':'command', 'command':'exit'}
    message_queue.put(message)
    
    
thread.start_new_thread(listener, ())

        
def main(argv):
    root = tk.Tk()
    root.title('WaveSyn-Interrupter')
    root.protocol('WM_DELETE_WINDOW', lambda:None)
    root.wm_attributes('-topmost', True)
    MainPanel(root).pack()

    queue_monitor = TkTimer(root, interval=250) 
    
    @queue_monitor.add_observer
    def queue_observer(*args, **kwargs):
        try:
            message = message_queue.get_nowait()
        except queue.Empty:
            return
         
        if message['type']=='command' and message['command']=='exit':
            root.deiconify()
            root.destroy()
            
    queue_monitor.active = True
        
    root.iconify()
    root.mainloop()



    

if __name__ == '__main__':
    main(None)