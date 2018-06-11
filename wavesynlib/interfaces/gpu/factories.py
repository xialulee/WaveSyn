# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 22:29:02 2018

@author: Feng-cong Li
"""
from reikna.fft import FFT
from reikna.linalg import MatrixMul, EntrywiseNorm
import numpy as np



class FFTFactory:
    @staticmethod
    def create(thr, size, dtype=np.complex128, axes=None, compile_=True):
        fft = FFT(thr.array(size, dtype=dtype), axes)
        if compile_:
            fft = fft.compile(thr)
        return fft
        
        
    def __init__(self):
        self.__cache    = {}        
        
        
    def __getitem__(self, key): 
        if key not in self.__cache:
            self.__cache[key] = self.create(*key)
        return self.__cache[key]
        
FFTFactory  = FFTFactory()



class MatrixMulFactory:
    @staticmethod
    def create(thr, a_size, b_size, dtype=np.complex128, compile_=True):
        mm = MatrixMul(thr.array(a_size, dtype=dtype), thr.array(b_size, dtype=dtype))
        if compile_:
            mm = mm.compile(thr)
        return mm
    
    
    def __init__(self):
        self.__cache = {}
        
        
    def __getitem__(self, key):
        if key not in self.__cache:
            self.__cache[key] = self.create(*key)
        return self.__cache[key]
    
MatrixMulFactory = MatrixMulFactory()



class EntrywiseNormFactory:
    @staticmethod
    def create(thr, size, axes=None, dtype=np.complex128, compile_=True):
        en = EntrywiseNorm(thr.array(size, dtype=dtype), axes=axes)
        if compile_:
            en = en.compile(thr)
        return en
    
    
    def __init__(self):
        self.__cache = {}
        
        
    def __getitem__(self, key):
        if key not in self.__cache:
            self.__cache[key] = self.create(*key)
        return self.__cache[key]
    
EntrywiseNormFactory = EntrywiseNormFactory()