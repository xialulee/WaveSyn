# -*- coding: utf-8 -*-
"""
Created on Fri Oct 09 17:15:41 2015

@author: Feng-cong Li
"""

import six.moves._thread as thread
from six.moves.queue import Queue

import reikna.cluda as cluda
from reikna.fft import FFT
import numpy as np

api = cluda.cuda_api()
#thr = api.Thread.create()

class FFTFactory(object):
    @staticmethod
    def createFFTProc(N, thr):
        return FFT(thr.array((N,), dtype=np.complex128)).compile(thr)
        
    def __init__(self):
        self.__cache    = {}        
        
    def __getitem__(self, key): # key = (N, thr)
        if key not in self.__cache:
            self.__cache[key]     = self.createFFTProc(*key)
        return self.__cache[key]
        
FFTFactory  = FFTFactory()


class Worker(object):
    def __init__(self):
        self.__messageIn    = Queue()
        self.__messageOut   = Queue()
        self.__thr          = None
        self.__active       = False        
        self.__occupied     = False
        
    @property
    def messageIn(self):
        return self.__messageIn
        
    @property
    def messageOut(self):
        return self.__messageOut
        
    @property
    def reiknaThread(self):
        return self.__thr
        
    @property
    def isActive(self):
        return self.__active
        
    @property 
    def isOccupied(self):
        return self.__occupied
    
    def activate(self):
        if not self.__active:
            thread.start_new_thread(self.threadFunc, ())
            self.__active   = True
    
    def threadFunc(self):
        self.__thr          = api.Thread.create()
        while True:
            msg     = self.messageIn.get()
            self.__occupied     = True
            try:
                command = msg['command']
                if command == 'exit':
                    break
                elif command == 'call':
                    func    = msg['callable object']
                    args    = msg['args']
                    kwargs  = msg['kwargs']
                    ret     = func(self, *args, **kwargs)
                    self.messageOut.put({'report':'function return', 'return value':ret})
            finally:
                self.__occupied     = False
        self.__thr.release()
        self.__active   = False