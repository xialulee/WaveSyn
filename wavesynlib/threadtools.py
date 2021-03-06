# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 14:05:12 2017

@author: Feng-cong Li
"""
import threading
from queue import Queue, Empty

from wavesynlib.languagecenter.wavesynscript import ModelNode
from wavesynlib.languagecenter.designpatterns import Singleton
from wavesynlib.languagecenter import datatypes



class _ThreadObj(threading.Thread):
    def __init__(self, func):
        self.__func = func
        super().__init__()
        self.__result = None
    
    
    def run(self):
        self.__result = self.__func()


    @property
    def result(self):
        if self.is_alive():
            return None
        else:
            return self.__result
        
        

# Will be used for GPU Worker. 
class _WaiterThread(threading.Thread):
    def __init__(self):
        self.__queue = Queue()
        super().__init__()
        
        
    def do(self, func):
        self.__queue.put(func)
    
    
    def run(self):
        queue = self.__queue
        while True:
            func = queue.get()
            func()
        
        
        
class _RepeaterThread(threading.Thread):
    def __init__(self, func):
        self.__repeat_func = func
        self.__queue = Queue()
        self.__call_once_finished = threading.Event()
        self.__call_once_retval = None
        super().__init__()
        
        
    def do_once(self, func):
        finished = self.__call_once_finished
        finished.clear()
        self.__queue.put(func)
        finished.wait()
        retval = self.__call_once_retval
        if isinstance(retval, Exception):
            raise retval
        else:
            return retval
    
    
    def run(self):
        queue = self.__queue
        repeat_func = self.__repeat_func
        while True:
            try:
                while True:
                    call_once_func = queue.get_nowait()
                    try:
                        retval = call_once_func()
                    except Exception as err:
                        self.__call_once_retval = err
                    else:
                        self.__call_once_retval = retval
                    finally:
                        self.__call_once_finished.set()
            except Empty:
                pass
            
            repeat_func()
        


# Only one thread manager for a process. 
class ThreadManager(ModelNode, metaclass=Singleton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Instance of ThreadManager must be intitialized in the main thread. 
        with self.attribute_lock:
            self.main_thread_id = threading.get_ident()
            
            
    @property
    def in_main_thread(self):
        return threading.get_ident() == self.main_thread_id
        
        
    def only_main_thread(self, block=True):
        raise NotImplementedError('Not implemented yet.')
        
        
    def main_thread_do(self, func=None, block=True):
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
            if func:
                return func()
            else:
                def run(func):
                    return func()
                return run
        else:
            def put_queue(func):
                slot = datatypes.CommandSlot(source='local', node_list=[func])
                self.root_node.command_queue.put(slot)
            
            if block:
                def block_do(func):
                    event = threading.Event()
                    return_box = []
                    def wrapper():
                        return_box.append(func())
                        event.set()
                    put_queue(wrapper)
                    event.wait()
                    return return_box[0]
                if func:
                    return block_do(func)
                else:
                    return block_do
            else:
                if func:
                    return put_queue(func)
                else:
                    return put_queue        
                
                
    def new_thread_do(self, func):
        thread_obj = _ThreadObj(func)
        thread_obj.start()
        return thread_obj
        
        
    def create_thread_object(self, func):
        return _ThreadObj(func)
    
    
    def create_repeater_thread(self, func):
        return _RepeaterThread(func)
        
