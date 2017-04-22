# -*- coding: utf-8 -*-
"""
Created on Fri Oct 09 14:00:27 2015

@author: Feng-cong Li
"""
from wavesynlib.mathtools import Algorithm
import wavesynlib.interfaces.gpu.cuda as wavesyncuda

import numpy as np

from pycuda.elementwise import ElementwiseKernel

magSquare   = ElementwiseKernel(
    'pycuda::complex<double> * output, pycuda::complex<double> * input',
    '''
output[i] = input[i] * pycuda::conj(input[i]);
    '''
) 

applyMask   = ElementwiseKernel(
    'pycuda::complex<double> * output, pycuda::complex<double> * origin, double * mask',
    '''
output[i] = origin[i] * mask[i];
    '''
)

realAndSqrt = ElementwiseKernel(
    'pycuda::complex<double> * output, pycuda::complex<double> * input',
    '''
double r = input[i].real();
r = r < 0.0 ? 0.0 : sqrt(r);
output[i] = r;    
    '''
)   

unimodularize = ElementwiseKernel(
    'pycuda::complex<double> * output, pycuda::complex<double> * input',
    '''
using namespace pycuda;
output[i] = polar(1.0, arg(input[i]));    
    '''
)

magAndPhi  = ElementwiseKernel(
    'pycuda::complex<double> * output, pycuda::complex<double> * mag, pycuda::complex<double> * phi',
    '''
using namespace pycuda;
output[i] = polar(abs(mag[i]), arg(phi[i]));    
    '''
)


class DIAC(Algorithm):
    __name__    = 'ISAA-DIAC (CUDA Impl)'
    __CUDA__    = True
    
    def __init__(self):
        super(DIAC, self).__init__()
        
    __parameters__  = (
        ['N', 'int', 'Sequence Length.'],
        ['Qr', 'expression', 'The interval in which correlation sidelobes are suppressed.'],
        ['K', 'int', 'Maximum iteration number.']
    )      
        
    def __call__(self, N, Qr, K): 
        thr = self.cuda_worker.reikna_thread
        twoN        = 2 * N
        fft         = wavesyncuda.FFTFactory[(twoN, thr)]
        
        mask        = np.ones((2*N,))
        mask[Qr]    = 0; mask[-Qr]   = 0
        mask        = thr.to_device(mask)
        
        cut         = np.zeros((N,)) + 1j * np.zeros((N,))
        cut         = thr.to_device(cut)
        
        s           = np.exp(1j * 2 * np.pi * np.random.rand(2*N))
        s[N:]       = 0
        s           = thr.to_device(s)
        Fs          = thr.array((2*N,), np.complex128)
        a           = thr.array((2*N,), np.complex128)
        
        for k in range(K):
            fft(Fs, s, 0) # Forward
            magSquare(a, Fs)
            fft(a, a, 1) # Inverse
            applyMask(a, a, mask)
            fft(a, a, 0) # Forward
            realAndSqrt(a, a)
            magAndPhi(a, a, Fs)
            fft(s, a, 1) # Inverse            
            unimodularize(s, s)
            s[N:]       = cut
            self.progress_checker(k, K, None)
        return s.get()[:N]        
        