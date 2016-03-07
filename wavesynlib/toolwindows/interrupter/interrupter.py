# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26 10:18:01 2016

@author: Feng-cong Li
"""
from __future__ import print_function, division, unicode_literals

import six.moves.tkinter as tk
import six.moves.tkinter_ttk as ttk

import json
import thread

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
    raw_input()
    exit_command = {'type':'command', 'command':'exit'}
    print(json.dumps(exit_command))    
    thread.interrupt_main()
    
    
thread.start_new_thread(listener, ())

        
def main(argv):
    root = tk.Tk()
    root.title('WaveSyn-Interrupter')
    root.protocol('WM_DELETE_WINDOW', lambda:None)
    root.wm_attributes('-topmost', True)
    MainPanel(root).pack()
    root.iconify()
    try:    
        root.mainloop()
    except KeyboardInterrupt:
        pass
    else:
        exit_command = {'type':'command', 'command':'exit'}
        print(json.dumps(exit_command))
    

if __name__ == '__main__':
    main(None)