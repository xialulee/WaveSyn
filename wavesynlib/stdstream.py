# -*- coding: utf-8 -*-
"""
Created on Sun Oct 26 21:06:35 2014

@author: Feng-cong Li
"""
import sys
import queue
import _thread as thread
from contextlib import contextmanager

from wavesynlib.languagecenter.designpatterns import  Observable

REALSTDOUT = sys.stdout
REALSTDERR = sys.stderr



class DumbStream:
    def write(self, content):
        pass
    
    def flush(self):
        pass
    
    
    
@contextmanager
def dumb_stream():
    backup_out = sys.stdout
    backup_err = sys.stderr
    sys.stdout = DumbStream()
    sys.stderr = DumbStream()
    try:
        yield
    finally:
        sys.stdout = backup_out
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
            
            

class StreamManager(Observable):
    class Stream:
        def __init__(self, manager, stream_type):
            self.__manager = manager
            self.__stream_type = stream_type
        def write(self, content, extras=None):
            self.__manager.queue.put((self.__stream_type, content, extras))
            
            
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
                self.notify_observers(stream_type, content, extras)
        except queue.Empty:
            pass