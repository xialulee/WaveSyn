# -*- coding: utf-8 -*-
"""
Created on Tue May 27 16:01:11 2014

@author: Feng-cong Li
"""
from numpy import *
from mathtools import Algorithm

class ALGOTEST(Algorithm):
    __name__    = 'ALGOTEST'
    def __init__(self):
        self.exitcond   = {}
        Algorithm.__init__(self)

    def initpoint(self, N):
        return exp(1j * 2 * pi * random.rand(N))
        
#    __parameters__  = (
#        ['N', 'int', 'Sequence Length.'],
#        ['Qr', 'expression', 'The interval in which correlation sidelobes are suppressed.'],
#        ['K', 'int', 'Maximum iteration number.']
#    )
    def __call__(self, A, B, C, D):
        s_init  = self.initpoint(A)
        return s_init