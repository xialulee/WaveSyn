# -*- coding: utf-8 -*-
"""
Created on Sun Oct 26 21:06:35 2014

@author: Feng-cong Li
"""

from wavesynlib.languagecenter.designpatterns import  Observable
import queue
import _thread as thread

import sys
REALSTDOUT  = sys.stdout
REALSTDERR  = sys.stderr



class StreamChain(object):
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
    class Stream(object):
        def __init__(self, manager, stream_type):
            self.__manager  = manager
            self.__stream_type   = stream_type
        def write(self, content):
            self.__manager.queue.put((self.__stream_type, content))
            
    def __init__(self):
        super(StreamManager, self).__init__()
        self.queue    = queue.Queue()
        self.__stdout   = StreamChain()
        self.__stdout   += REALSTDOUT
        self.__stdout   += self.Stream(self, 'STDOUT')
        
        self.__stderr   = StreamChain()
        self.__stderr   += REALSTDERR
        self.__stderr   += self.Stream(self, 'STDERR')
        
        sys.stdout = self.__stdout
        sys.stderr = self.__stderr
        
    def write(self, content, stream_type='STDOUT'):
        self.queue.put((stream_type, content))
        
    def update(self): # Usually called by a timer.
        try:
            while True:
                stream_type, content = self.queue.get_nowait()
                self.notify_observers(stream_type, content)
        except queue.Empty:
            pass