# -*- coding: utf-8 -*-
"""
Created on Fri Oct 09 14:00:27 2015

@author: Feng-cong Li
"""
from wavesynlib.mathtools import Algorithm, Expression
from wavesynlib.mathtools import Parameter as algo_param
import wavesynlib.interfaces.gpu.cuda as wavesyncuda

import numpy as np

from pycuda.elementwise import ElementwiseKernel
from reikna.core import Transformation, Parameter, Annotation, Type



mag_square   = ElementwiseKernel(
    'pycuda::complex<double> * output, const pycuda::complex<double> * input',
    '''
output[i] = input[i] * pycuda::conj(input[i]);
    '''
)
 

apply_mask   = ElementwiseKernel(
    'pycuda::complex<double> * output, const pycuda::complex<double> * origin, const double * mask',
    '''
output[i] = origin[i] * mask[i];
    '''
)


combine_mag_phi = ElementwiseKernel(
    'pycuda::complex<double> * output, const pycuda::complex<double> * mag_square, const pycuda::complex<double> * phase',
    '''
using namespace pycuda;

double r = mag_square[i].real();
r = r < 0.0 ? 0.0 : sqrt(r);

output[i] = polar(r, arg(phase[i]));
    '''
)


unimodularize = ElementwiseKernel(
    'pycuda::complex<double> * output, const pycuda::complex<double> * input, const int N', 
    '''
using namespace pycuda;
output[i] = i>=N ? complex<double>(0.0) : polar(1.0, arg(input[i]));    
    '''
)



class DIAC(Algorithm):
    __name__ = 'ISAA-DIAC (CUDA Impl)'
    __CUDA__ = True
    __cache = {}
    
    def __init__(self):
        super().__init__()
        
        
    def __get_procs(self, thr, N):
        if N not in self.__cache:
            fft = wavesyncuda.FFTFactory.create_fft_proc(thr, (N,), compile_=False)
            unimod_trans = Transformation(
                [Parameter('output', Annotation(Type(np.complex128, N), 'o')),
                Parameter('input', Annotation(Type(np.complex128, N), 'i'))],
                """
                double2 val = ${input.load_same};
                double angle = atan2(val.y, val.x);
                val.x = cos(angle);
                val.y = sin(angle);
                ${output.store_same}(val);
                """)
            fft.parameter.output.connect(unimod_trans, unimod_trans.input, uni=unimod_trans.output)
            fft_unimod = fft.compile(thr)
            self.__cache[N] = fft_unimod
        return self.__cache[N]
        
                
    def __call__(self, 
                 N: algo_param(int, 'Sequence Length.'), 
                 Qr: algo_param(Expression, 'The interval in which correlation sidelobes are suppressed.'), 
                 K: algo_param(int, 'Maximum iteration number')): 
        thr = self.cuda_worker.reikna_thread
        twoN = 2 * N
        fft = wavesyncuda.FFTFactory[(thr, (twoN,))]
        
        mask        = np.ones((2*N,))
        mask[Qr]    = 0; mask[-Qr]   = 0
        mask        = thr.to_device(mask)
        
        cut         = np.zeros((N,)) + 1j * np.zeros((N,))
        cut         = thr.to_device(cut)
        
        s           = np.exp(1j * 2 * np.pi * np.random.rand(twoN))
        s[N:]       = 0
        s           = thr.to_device(s)
        Fs          = thr.array((2*N,), np.complex128)
        a           = thr.array((2*N,), np.complex128)
        
        for k in range(K):
            fft(Fs, s, 0) # Forward
            mag_square(a, Fs)
            fft(a, a, 1) # Inverse
            apply_mask(a, a, mask)
            fft(a, a, 0) # Forward
            combine_mag_phi(a, a, Fs)
            fft(s, a, 1) # Inverse            
            unimodularize(s, s, N)
            self.progress_checker(k, K, None)
        return s.get()[:N]        
        