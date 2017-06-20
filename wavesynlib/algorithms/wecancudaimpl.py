# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 21:24:25 2017

@author: Feng-cong Li
"""

from wavesynlib.mathtools import Algorithm
import wavesynlib.interfaces.gpu.cuda as wavesyncuda

import numpy as np
from scipy import linalg

from pycuda.elementwise import ElementwiseKernel
from pycuda import gpuarray



unimodularize = ElementwiseKernel(
    'pycuda::complex<double> * output, const pycuda::complex<double> * input, const int N', 
    '''
using namespace pycuda;
output[i] = i>=N ? complex<double>(0.0) : polar(1.0, arg(input[i]));    
    '''
)



class WeCAN(Algorithm):
    __name__ = 'WeCAN (CUDA Impl)'
    __CUDA__ = True
    
    
    def __init__(self):
        super().__init__()
        
        
    __parameters__ = (
        ['N', 'int', 'Sequence Length N.'],
        ['gamma', 'expression', 'N-by-1, corresponding to weights w_k = gamma_k^2'],
        ['e', 'float', 'Threashold for exit condition.'],
        ['K', 'int', 'Maximum iteration number.'])
    def __call__(self, N, gamma, e, K):
        thr = self.cuda_worker.reikna_thread
        s = np.exp(1j * 2 * np.pi * np.random.rand(2*N), dtype=np.complex128)
        s.shape = (N, 1)
        # s_prev = np.zeros((N,), dtype=np.complex128)
        gamma[0] = 0
        Gamma = linalg.toeplitz(gamma)
        eigvalues = linalg.eig(Gamma)[0]
        gamma[0] = abs(eigvalues.min())
        Gamma = linalg.toeplitz(gamma) / gamma[0]
        C = linalg.sqrtm(Gamma).T
        
        C = thr.to_device(C)
        Alpha = gpuarray.zeros((2*N, N), dtype=np.complex128)
        Z = gpuarray.zeros((2*N, N), dtype=np.complex128)
        F = gpuarray.zeros((2*N, N), dtype=np.complex128)
        s = thr.to_device(s)
        rep_s = gpuarray.empty((N, N), dtype=np.complex128)
        ones = thr.to_device(np.ones(N,), dtype=np.complex128)
        fft = wavesyncuda.FFTFactory[(thr, (2*N, N), [0])]
        outer = wavesyncuda.MatrixMulFactory[(thr, (N, 1), (1, N))]
        
        
        for k in range(K):
            outer(rep_s, s, ones)
            Z[:, :N] = C * rep_s
            fft(F, Z)
        