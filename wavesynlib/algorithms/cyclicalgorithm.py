# -*- coding: utf-8 -*-
"""
Created on Thu May 29 09:28:31 2014

@author: Feng-cong Li
"""
from mathtools import Operator, Algorithm
from numpy import *
from numpy.fft.fftpack import fft, ifft


@Operator
def Proj_M1(s): # This function is corresponding to eq.22.
    return exp(1j * angle(s)) # see eq.22
    
    
@Operator    
def Proj_F1(s):
    N   = len(s)
    return ifft(Proj_M1(fft(s, 2*N)))[0:N]
    
    
class CAN(Algorithm):
    __name__    = 'CAN'
    def __init__(self):
        super(CAN, self).__init__()

    def initpoint(self, N):
        return exp(1j * 2 * pi * random.rand(N))
        
    __parameters__  = (
        ['N', 'int', 'Sequence Length.'],
        ['e', 'float', 'Threshold for exit iteration.'],
        ['K', 'int', 'Maximum iteration number.']
    )
    def __call__(self, N, e, K):
        s_init  = self.initpoint(N)       
        Tcan   = (Proj_M1 * Proj_F1) ** K
        Tcan.iterThreshold  = e
        Tcan.progressChecker   = self.progressChecker
        return Tcan(s_init)