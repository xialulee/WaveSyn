# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26 10:42:50 2016

@author: Feng-cong Li
"""

from __future__ import print_function, division, unicode_literals

from wavesynlib.languagecenter.wavesynscript import ModelNode
from wavesynlib import status
from wavesynlib.toolwindows.interrupter import interrupter

import six.moves._thread as thread
#import threading

from six.moves import queue
import multiprocessing as mp


#_is_alive = threading.Event()
_messages_from_interrupter = mp.Queue()
_messages_to_interrupter = mp.Queue()

def _listener():    
    while True:
        try:
            command = _messages_from_interrupter.get_nowait()
        except queue.Empty:
            continue
        if command['type'] == 'command':
            if command['command'] == 'exit':
                break
            elif command['command'] == 'interrupt_main_thread':
                if status.is_busy():
                    thread.interrupt_main()
#    _is_alive.set()


def _launch_interrupter(messages_from_interrupter, messages_to_interrupter):
    interrupter.main(messages_from_interrupter, messages_to_interrupter)


class InterrupterNode(ModelNode):
    def __init__(self, *args, **kwargs):
        ModelNode.__init__(self, *args, **kwargs)
        p = mp.Process(target=_launch_interrupter, args=(_messages_from_interrupter, _messages_to_interrupter))
        thread.start_new_thread(_listener, ())
        self.__process = p

    
    def launch(self):
        if not self.__process.is_alive():
            self.__process.start()
        
    
    def close(self):
#        if not _is_alive.is_set():
        _messages_to_interrupter.put({'type':'command', 'command':'exit'})
#        self.__process.terminate()
