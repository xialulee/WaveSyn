# -*- coding: utf-8 -*-
"""
Created on Fri Oct 09 14:00:27 2015

@author: Feng-cong Li
"""
from wavesynlib.mathtools import Algorithm, Expression
from wavesynlib.mathtools import Parameter as algo_param
from wavesynlib.interfaces.gpu.factories import FFTFactory

import numpy as np
from functools import lru_cache

#from pycuda.elementwise import ElementwiseKernel
from reikna.core import Transformation, Parameter, Annotation, Type
from reikna.cluda import functions
from reikna.algorithms import PureParallel



#mag_square   = ElementwiseKernel(
#    'pycuda::complex<double> * output, const pycuda::complex<double> * input',
#    '''
#output[i] = input[i] * pycuda::conj(input[i]);
#    '''
#)
 

#apply_mask   = ElementwiseKernel(
#    'pycuda::complex<double> * output, const pycuda::complex<double> * origin, const double * mask',
#    '''
#output[i] = origin[i] * mask[i];
#    '''
#)


#combine_mag_phi = ElementwiseKernel(
#    'pycuda::complex<double> * output, const pycuda::complex<double> * mag_square, const pycuda::complex<double> * phase',
#    '''
#using namespace pycuda;
#
#double r = mag_square[i].real();
#r = r < 0.0 ? 0.0 : sqrt(r);
#
#output[i] = polar(r, arg(phase[i]));
#    '''
#)


#unimodularize = ElementwiseKernel(
#    'pycuda::complex<double> * output, const pycuda::complex<double> * input, const int N', 
#    '''
#using namespace pycuda;
#output[i] = i>=N ? complex<double>(0.0) : polar(1.0, arg(input[i]));    
#    '''
#)



@lru_cache()    
def get_procs(thr, N):
    fft = FFTFactory.create(thr, (N,), compile_=False)
    unimod_trans = Transformation(
        [Parameter('output', Annotation(Type(np.complex128, N), 'o')),
        Parameter('input', Annotation(Type(np.complex128, N), 'i'))],
        """
VSIZE_T idx = ${idxs[0]};
${input.ctype} val = ${input.load_same};
if (idx>${N}/2){
    val.x = 0.0;
    val.y = 0.0;
    ${output.store_same}(val);
}else
    ${output.store_same}(${polar_unit}(atan2(val.y, val.x)));
        """,
        render_kwds=dict(polar_unit=functions.polar_unit(dtype=np.float64), N=N)
    )
    fft.parameter.output.connect(unimod_trans, unimod_trans.input, uni=unimod_trans.output)
    fft_unimod = fft.compile(thr)
    
    mag_square = PureParallel(
        [Parameter('output', Annotation(Type(np.complex128, N), 'o')),
         Parameter('input', Annotation(Type(np.complex128, N), 'i'))],
        '''
VSIZE_T idx = ${idxs[0]};
${input.ctype} val = ${input.load_idx}(idx);  
val.x = val.x*val.x + val.y*val.y;
val.y = 0;
${output.store_idx}(idx, val);
        '''
    )
    mag_square = mag_square.compile(thr)
    
    apply_mask = PureParallel(
        [Parameter('output', Annotation(Type(np.complex128, N), 'o')),
         Parameter('origin', Annotation(Type(np.complex128, N), 'i')),
         Parameter('mask', Annotation(Type(np.double, N), 'i'))],
        '''
VSIZE_T idx = ${idxs[0]};
${output.store_idx}(idx, ${mul}(${origin.load_idx}(idx), ${mask.load_idx}(idx)));        
        ''',
        render_kwds=dict(mul=functions.mul(np.complex128, np.double))
    )
    apply_mask = apply_mask.compile(thr)
    
    combine_mag_phi = PureParallel(
        [Parameter('output', Annotation(Type(np.complex128, N), 'o')),
         Parameter('mag_square', Annotation(Type(np.complex128, N), 'i')),
         Parameter('phase', Annotation(Type(np.complex128, N), 'i'))],
        '''
VSIZE_T idx = ${idxs[0]};
double r = ${mag_square.load_idx}(idx).x;  
r = r<0.0 ? 0.0 : ${pow}(r, 0.5);
double2 v = ${phase.load_idx}(idx);
double angle = atan2(v.y, v.x);
${output.store_idx}(idx, ${polar}(r, angle));
        ''',
        render_kwds=dict(pow=functions.pow(np.double), polar=functions.polar(np.double))
    )
    combine_mag_phi = combine_mag_phi.compile(thr)
   
    return fft_unimod, mag_square, apply_mask, combine_mag_phi



class DIAC(Algorithm):
    __name__ = 'ISAA-DIAC (CUDA Impl)'
    __CUDA__ = True
    
    def __init__(self):
        super().__init__()
        
    
    def __call__(self, 
                 N: algo_param(int, 'Sequence Length.'), 
                 Qr: algo_param(Expression, 'The interval in which correlation sidelobes are suppressed.'), 
                 K: algo_param(int, 'Maximum iteration number')): 
        thr = self.cuda_worker.reikna_thread
        twoN = 2 * N
        fft = FFTFactory[(thr, (twoN,))]
        fft_unimod, mag_square, apply_mask, combine_mag_phi = get_procs(thr, twoN)
        
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
#            fft(s, a, 1) # Inverse            
#            unimodularize(s, s, N)
            fft_unimod(s, a, 1)
            self.progress_checker(k, K, None)
        return s.get()[:N]        
        