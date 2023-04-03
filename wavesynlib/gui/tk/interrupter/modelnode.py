# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26 10:42:50 2016

@author: Feng-cong Li
"""
from wavesynlib.languagecenter.wavesynscript import ModelNode
from wavesynlib import status
from . import window

import _thread as thread
import multiprocessing as mp



_messages_from_interrupter = mp.Queue()
_messages_to_interrupter = mp.Queue()



def _listener():    
    while True:
        command = _messages_from_interrupter.get()
        if command['type'] == 'command':
            if command['command'] == 'exit':
                break
            elif command['command'] == 'interrupt_main_thread':
                if status.is_busy():
                    thread.interrupt_main()



def _launch_interrupter(messages_from_interrupter, messages_to_interrupter):
    window.main(messages_from_interrupter, messages_to_interrupter)



class InterrupterNode(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def on_connect(self):
        super().on_connect()
        p = mp.Process(
                target=_launch_interrupter, 
                args=(_messages_from_interrupter, _messages_to_interrupter))
        self.root_node.thread_manager.new_thread_do(_listener)
        self.__process = p

    
    def launch(self):
        if not self.__process.is_alive():
            self.__process.start()
        
    
    def close(self):
        message = {'type':'command', 'command':'exit'}
        _messages_from_interrupter.put(message) # Terminate _listener thread. 
        _messages_to_interrupter.put(message) # Terminate interrupter process.

