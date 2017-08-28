# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 14:05:12 2017

@author: Feng-cong Li
"""
import _thread as thread
import threading

from wavesynlib.languagecenter.wavesynscript import ModelNode
from wavesynlib.languagecenter.designpatterns import Singleton
from wavesynlib.languagecenter import datatypes



class _ThreadObj(threading.Thread):
    def __init__(self, func):
        self.__func = func
        threading.Thread.__init__(self)
    
    
    def run(self):
        self.__func()


# Only one thread manager for a process. 
class ThreadManager(ModelNode, metaclass=Singleton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Instance of ThreadManager must be intitialized in the main thread. 
        with self.attribute_lock:
            self.main_thread_id = thread.get_ident()
            
            
    @property
    def in_main_thread(self):
        return thread.get_ident() == self.main_thread_id
        
        
    def only_main_thread(self, block=True):
        pass
        
        
    def main_thread_do(self, block=True):
        '''Usage:
@main_thread_do(block=False)
def do_something():
  pass
  
do_something will be called in the main thread in nonblocking mode.

@main_thread_do()
def do_something():
  pass
  
do_something will be called in the main thread in blocking mode, i.e., 
the rest code will not be executed util do_something() returned. 
'''
        if self.in_main_thread:
            def run(func):
                func()
            return run
        else:
            def put_queue(func):
                slot = datatypes.CommandSlot(source='local', node_list=[func])
                self.root_node.command_queue.put(slot)
            
            if block:
                def block_do(func):
                    event = threading.Event()
                    def wrapper():
                        func()
                        event.set()
                    put_queue(wrapper)
                    event.wait()
                return block_do
            else:
                return put_queue        
                
                
    def new_thread_do(self, func):
        return thread.start_new_thread(func, (), {})
        
        
    def create_thread_object(self, func):
        return _ThreadObj(func)
        
