# -*- coding: utf-8 -*-
"""
Created on Fri Oct 09 17:15:41 2015

@author: Feng-cong Li
"""

import six.moves._thread as thread
from six.moves.queue import Queue

import reikna.cluda as cluda
from reikna.fft import FFT
from reikna.linalg import MatrixMul, EntrywiseNorm
import numpy as np


from wavesynlib.languagecenter.wavesynscript import ModelNode


api = cluda.cuda_api()


class FFTFactory:
    @staticmethod
    def create_fft_proc(thr, size, axes=None, compile_=True):
        fft = FFT(thr.array(size, dtype=np.complex128), axes)
        if compile_:
            fft = fft.compile(thr)
        return fft
        
        
    def __init__(self):
        self.__cache    = {}        
        
        
    def __getitem__(self, key): # key = (N, thr)
        if key not in self.__cache:
            self.__cache[key] = self.create_fft_proc(*key)
        return self.__cache[key]
        
FFTFactory  = FFTFactory()



class MatrixMulFactory:
    @staticmethod
    def create_matrixmul_proc(thr, a_size, b_size, dtype=np.complex128, compile_=True):
        mm = MatrixMul(thr.array(a_size, dtype=dtype), thr.array(b_size, dtype=dtype))
        if compile_:
            mm = mm.compile(thr)
        return mm
    
    
    def __init__(self):
        self.__cache = {}
        
        
    def __getitem__(self, key):
        if key not in self.__cache:
            self.__cache[key] = self.create_matrixmul_proc(*key)
        return self.__cache[key]
    
MatrixMulFactory = MatrixMulFactory()



class EntrywiseNormFactory:
    @staticmethod
    def create_entrywisenorm_proc(thr, size, axes=None, dtype=np.complex128, compile_=True):
        en = EntrywiseNorm(thr.array(size, dtype=dtype), axes=axes)
        if compile_:
            en = en.compile(thr)
        return en
    
    
    def __init__(self):
        self.__cache = {}
        
        
    def __getitem__(self, key):
        if key not in self.__cache:
            self.__cache[key] = self.create_entrywisenorm_proc(*key)
        return self.__cache[key]
    
EntrywiseNormFactory = EntrywiseNormFactory()



class Worker(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__message_in = Queue()
        self.__message_out = Queue()
        self.__thr = None
        self.__active = False        
        self.__busy = False
        
        
    @property
    def message_in(self):
        return self.__message_in
        
        
    @property
    def message_out(self):
        return self.__message_out
        
        
    @property
    def reikna_thread(self):
        return self.__thr
        
        
    @property
    def is_active(self):
        return self.__active
        
        
    @property 
    def is_busy(self):
        return self.__busy
        
    
    def activate(self):
        if not self.__active:
            thread.start_new_thread(self.__thread_func, ())
            self.__active   = True
            
    
    def __thread_func(self):
        self.__thr = api.Thread.create()
        while True:
            msg     = self.message_in.get()
            self.__busy = True
            try:
                command = msg['command']
                if command == 'exit':
                    break
                elif command == 'call':
                    func    = msg['callable object']
                    args    = msg['args']
                    kwargs  = msg['kwargs']
                    ret = func(*args, **kwargs)
                    self.message_out.put({'report':'function return', 'return value':ret})
            finally:
                self.__busy = False
        self.__thr.release()
        self.__active   = False
        