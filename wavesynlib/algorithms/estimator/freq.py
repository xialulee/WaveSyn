# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 14:24:23 2015

@author: Feng-cong Li

Originally posted on http://blog.sina.com.cn/s/blog_4513dde60100o6na.html
"""
from numpy import abs, angle, array, atleast_1d, \
    complex128, correlate, exp, isscalar, pi, r_, \
    roots, sort, sqrt, zeros

from numpy.linalg import eigh, eigvals, pinv
from numpy.random import randn

import hy
from .hyfreq import *
from wavesynlib.formulae.noise import complex_gaussian


autocorrelate   = lambda x: correlate(x, x, mode='full')
    
    
    
#def root_MUSIC(Rx, p):
    #'''Estimate signal frequencies using root-MUSIC algorithm
    #Rx: auto-correlation matrix of signal;
    #p:  number of complex sinusoids;
    #return value: normalized frequencies.
    #'''
    #p       = int(p)
    #N       = Rx.shape[0]
    #D, U    = eigh(Rx) # Notice! Ascending order!
    #M       = N - p # The dimension of the noise subspace.
    #Un      = array(U[:, :M]) # orthonormal basis of the noise subspace.    
    #P       = sum(autocorrelate(Un[:, k]) for k in range(M))
    #rootsP  = roots(P)
    ## Remove all the roots outside the unit circle
    #rootsP  = rootsP[(abs(rootsP)<=1).nonzero()]
    ## Sort roots with respect to its distance to the unit circle
    #rootsP  = rootsP[(abs(abs(rootsP) - 1)).argsort()]
    #return angle(rootsP[:p]) / 2 / pi
    
    

def genTestSig(n, freqs, amps, noisePow):
    '''Generate a testing signal.
    n:          sample indices;
    freqs:      normalized frequencies of complex sinusoids;
    amps:       amplitudes of complex sinusoids;
    noisePow:   additive white Gaussian noise power;
    return value: signal vector.
    '''
    if isscalar(n):
        n   = r_[:n]
    x       = complex128(zeros((len(n), )))
    freqs   = atleast_1d(freqs)
    amps    = atleast_1d(amps)
    for freq, amp in zip(freqs, amps):
        x += amp * exp(1j * 2 * pi * freq * n)
    #awgn    = sqrt(noisePow/2) * randn(len(n)) + 1j * sqrt(noisePow/2) * randn(len(n))
    awgn = complex_gaussian(len(n), noisePow)
    return x + awgn
    


if __name__ == '__main__':
    freqs       = [0.1, 0.18, 0.25]
    amps        = [1, 1, 1]
    noisePow    = 0.1
    N           = 10
    print(f'{len(freqs)} complex sinusoids are presented in additive white Gaussian noise.')
    print('Amplitudes of these sinusoids are:', amps)
    print('Frequencies of these sinusoids are:', freqs)
    print('Power of additive white Gaussian noise is', noisePow)
    x           = genTestSig(N, freqs, amps, noisePow)
    R           = Rx(x)
    print('Estimated frequencies (ESPRIT) are:    ', sort(LS_ESPRIT(R, len(freqs))))
    print('Estimated frequencies (root-MUSIC) are:', sort(root_MUSIC(R, len(freqs))))
    