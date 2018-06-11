# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 21:24:25 2017

@author: Feng-cong Li
"""

from wavesynlib.mathtools import Algorithm, Expression, Parameter
from wavesynlib.interfaces.gpu.factories import FFTFactory, MatrixMulFactory, EntrywiseNormFactory

from math import sqrt
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
        
        
    def __call__(self, 
                 N: Parameter(int, 'Sequence Length N.'), 
                 gamma: Parameter(Expression, 'N-by-1, corresponding to weights w_k = gamma_k^2'), 
                 e: Parameter(float, 'Threashold for exit condition.'), 
                 K: Parameter(int, 'Maximum iteration number.')):
        thr = self.cuda_worker.reikna_thread
        s = np.exp(1j * 2 * np.pi * np.random.rand(N), dtype=np.complex128)
        iterdiff = thr.to_device(np.zeros((1,), dtype=np.double))
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
        s_prev = thr.empty_like(s)
        rep_s = gpuarray.empty((N, N), dtype=np.complex128)
        ones = thr.to_device(np.ones(N, dtype=np.complex128))
        sqrtNrv = thr.to_device(np.ones(N, dtype=np.double)/sqrt(N))
        fnorm = gpuarray.zeros((2*N, 1), dtype=np.double)
        fnormmat = gpuarray.zeros((2*N, N), dtype=np.double)
        
        fft = FFTFactory[(thr, (2*N, N), (0,))]
        outer = MatrixMulFactory[(thr, (N, 1), (1, N))]
        rep = MatrixMulFactory[(thr, (2*N, 1), (1, N), np.double)]
        sum_ = MatrixMulFactory[(thr, (N, N), (N, 1))]
        rownorm = EntrywiseNormFactory[(thr, (2*N, N), (1,))]
        vecnorm = EntrywiseNormFactory[(thr, (N,))]
        
        
        for k in range(K):
            s_prev[:] = s
            outer(rep_s, s, ones)
            Z[:N, :] = C * rep_s
            fft(F, Z)
            rownorm(fnorm, F)
            rep(fnormmat, fnorm, sqrtNrv)
            Alpha[:, :] = F / fnormmat
            fft(Alpha, Alpha, 1)
            rep_s[:, :] = C.conj() * Alpha[:N, :]
            sum_(s, rep_s, ones)
            unimodularize(s, s, N)
            vecnorm(iterdiff, s-s_prev)
            if iterdiff.get() <= e:
                break
            self.progress_checker(k, K, None)
            
        return s.get()
        