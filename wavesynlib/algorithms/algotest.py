# -*- coding: utf-8 -*-
"""
Created on Tue May 27 16:01:11 2014

@author: Feng-cong Li
"""
from numpy import *
from wavesynlib.mathtools import Algorithm, Expression, Parameter

class ALGOTEST(Algorithm):
    __name__    = 'ALGOTEST'
    def __init__(self):
        self.exitcond   = {}
        Algorithm.__init__(self)


    def initpoint(self, N):
        return exp(1j * 2 * pi * random.rand(N))
        

    def __call__(self, 
                 A: Parameter(int, 'first'), 
                 B: Parameter(Expression, 'second'), 
                 C: Parameter(float, 'third'), 
                 D: Parameter(float, 'fourth')):
        s_init  = self.initpoint(A)
        return s_init