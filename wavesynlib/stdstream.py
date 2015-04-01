# -*- coding: utf-8 -*-
"""
Created on Sun Oct 26 21:06:35 2014

@author: Feng-cong Li
"""

from wavesynlib.common     import  Observable
import Queue

import sys
REALSTDOUT  = sys.stdout
REALSTDERR  = sys.stderr

class StreamChain(object):
    def __init__(self):
        self.__streamlist   = []

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
        for stream in self.__streamlist:
            stream.write(content)

class StreamManager(Observable):
    class Stream(object):
        def __init__(self, manager, streamType):
            self.__manager  = manager
            self.__streamType   = streamType
        def write(self, content):
            self.__manager.queue.put((self.__streamType, content))
            
    def __init__(self):
        super(StreamManager, self).__init__()
        self.queue    = Queue.Queue()
        self.__stdout   = StreamChain()
        self.__stdout   += REALSTDOUT
        self.__stdout   += self.Stream(self, 'STDOUT')
        
        self.__stderr   = StreamChain()
        self.__stderr   += REALSTDERR
        self.__stderr   += self.Stream(self, 'STDERR')
        
        sys.stdout = self.__stdout
        sys.stderr = self.__stderr
        
    def write(self, content, streamType='STDOUT'):
        self.queue.put((streamType, content))
        
    def update(self):
        try:
            while True:
                streamType, content = self.queue.get_nowait()
                self.notifyObservers(streamType, content)
        except Queue.Empty:
            pass