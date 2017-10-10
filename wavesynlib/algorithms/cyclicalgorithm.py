# -*- coding: utf-8 -*-
"""
Created on Thu May 29 09:28:31 2014

@author: Feng-cong Li
"""
from wavesynlib.mathtools import Algorithm, Parameter
from wavesynlib.languagecenter.wavesynscript.math import Operator
from numpy import angle, exp, pi, random
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
        super().__init__()


    def initpoint(self, N):
        return exp(1j * 2 * pi * random.rand(N))
        

    def __call__(self, 
                 N: Parameter(int, 'Sequence Length.'), 
                 e: Parameter(float, 'Threashold for exit iteration.'), 
                 K: Parameter(int, 'Maximum iteration number.')):
        s_init  = self.initpoint(N)       
        Tcan   = (Proj_M1 * Proj_F1) ** K
        Tcan.iterThreshold  = e
        Tcan.progress_checker   = self.progress_checker
        return Tcan(s_init)