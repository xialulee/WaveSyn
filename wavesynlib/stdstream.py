# -*- coding: utf-8 -*-
"""
Created on Sun Oct 26 21:06:35 2014

@author: Feng-cong Li
"""
import sys
import queue
import _thread as thread
from contextlib import contextmanager

from wavesynlib.languagecenter.datatypes import Event
from wavesynlib.languagecenter.designpatterns import  Observable
from wavesynlib.languagecenter.wavesynscript import ModelNode

REALSTDOUT = sys.stdout
REALSTDERR = sys.stderr



class DumbStream:
    def write(self, content):
        pass
    
    def flush(self):
        pass
    
    
    
@contextmanager
def dumb_stream(stdout=True, stderr=True):
    backup_out = sys.stdout
    backup_err = sys.stderr
    try:
        if stdout:
            sys.stdout = DumbStream()
        if stderr:
            sys.stderr = DumbStream()
        yield
    finally:
        if stdout:
            sys.stdout = backup_out
        if stderr:
            sys.stderr = backup_err



class StreamChain:
    def __init__(self):
        self.__streamlist   = []
        self.__lock = thread.allocate_lock()
        

    def __iadd__(self, stream):
        self.__streamlist.append(stream)
        return self
    

    def remove(self, stream):
        while True:
            try:
                del self.__streamlist[self.__streamlist.index(stream)]
            except ValueError:
                break
            

    def write(self, content):
        with self.__lock:
            for stream in self.__streamlist:
                stream.write(content)
                
            
    def flush(self):
        for stream in self.__streamlist:
            try:
                stream.flush()
            except AttributeError: 
                # For Python 3, this happens when closing WaveSyn.
                pass
            
            

class StreamManager(ModelNode, Observable):
    class Stream:
        def __init__(self, manager, stream_type):
            self.__manager = manager
            self.__stream_type = stream_type
        def write(self, content, extras=None):
            self.__manager.queue.put((self.__stream_type, content, extras))
            
            # If the write is called by code in main thread, 
            # notify observers immediately. 
            if thread.get_ident() == self.__manager.root_node.thread_manager.main_thread_id:
                self.__manager.update()
            
            
    def __init__(self):
        super().__init__()
        self.queue = queue.Queue()
        self.__stdout = StreamChain()
        self.__stdout += REALSTDOUT
        self.__stdout += self.Stream(self, 'STDOUT')
        
        self.__stderr = StreamChain()
        self.__stderr += REALSTDERR
        self.__stderr += self.Stream(self, 'STDERR')
        
        sys.stdout = self.__stdout
        sys.stderr = self.__stderr
        
        
    def write(self, content, stream_type='STDOUT', extras=None):
        self.queue.put((stream_type, content, extras))
        
        
    def update(self): # Usually called by a timer.
        try:
            while True:
                stream_type, content, extras = self.queue.get_nowait()
                self.notify_observers(Event(
                    sender = self,
                    kwargs = {
                        "stream_type": stream_type,
                        "content":     content,
                        "extras":      extras}))
        except queue.Empty:
            pass