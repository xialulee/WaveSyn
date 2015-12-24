# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 14:24:23 2015

@author: Feng-cong Li

Originally posted on http://blog.sina.com.cn/s/blog_4513dde60100o6na.html
"""
from __future__   import division, print_function

import itertools

from numpy        import abs, angle, array, atleast_1d, complex128, correlate, exp, isscalar, mat, pi, r_, roots, sort, sqrt, zeros

from numpy.linalg import eigh, eigvals, pinv
from numpy.random import randn


autocorrelate   = lambda x: correlate(x, x, mode='full')


def Rx(x, m=None):
    '''Estimate autocorrelation matrix of vector x
    x:  signal vector
    m:  size of Rx
    return value: estimated autocorrelation matrix
    '''
    N = len(x)
    if m == None:
        m = N
    elif m > N:
        raise ValueError("The number of rows/columns of R should less than or equal to vector lenght N.")
    # generate a indices matrix, as
    # 0 -1 -2 -3 ...
    # 1  0 -1 -2 ...
    # 2  1  0 -1 ...
    # 3  2  1  0 ...
    # ...    
    indices     = r_['c', :m] - r_['r', :m]
    # Please use newest version of numpy.
    # Since the old version calculates correlate without conjugate for complex vectors.
    acHat       = autocorrelate(x)
    # using autocorrelation samples and indices matrix to create Rx
    # Rx =
    #   r[ 0] r[-1] r[-2] r[-3] ...
    #   r[ 1] r[ 0] r[-1] r[-2] ...
    #   r[ 2] r[ 1] r[ 0] r[-1] ...
    #   r[ 3] r[ 2] r[ 1] r[ 0] ...
    #   ..    
    return acHat[indices + N - 1] / N
    
def LS_ESPRIT(Rx, p):
    '''Estimate signal frequencies using LS-ESPRIT algorithm
    Rx: autocorrelation matrix of signal;
    p:   number of complex sinusoids;
    return value: normalized frequencies.
    '''
    p       = int(p)
    Rx      = mat(Rx)
    N       = Rx.shape[0]
    # eigh is a newly added function in numpy 1.8.0 which calculates the eigenvalue and eigenvectors efficiently for Hermitian matrix. 
    D, U    = eigh(Rx)
    # Obtain signal subspace from U
    # Unlike numpy.linalg.svd, the eigenvalue and the corresponding eigenvectors calculated by eigh are in ascending order. 
    Usig    = U[:, (N-p):]
    # 
    U0      = mat(Usig[:N-1, :])
    U1      = mat(Usig[1:, :])
    # Eigenvalues of U1\U0
    return -angle(eigvals(pinv(U1)*U0)) / 2 / pi
    
    
    
def root_MUSIC(Rx, p):
    '''Estimate signal frequencies using root-MUSIC algorithm
    Rx: auto-correlation matrix of signal;
    p:  number of complex sinusoids;
    return value: normalized frequencies.
    '''
    p       = int(p)
    N       = Rx.shape[0]
    D, U    = eigh(Rx) # Notice! Ascending order!
    M       = N - p # The dimension of the noise subspace.
    Un      = array(U[:, :M]) # orthonormal basis of the noise subspace.    
    P       = sum(autocorrelate(Un[:, k]) for k in range(M))
    rootsP  = roots(P)
    # Remove all the roots outside the unit circle
    rootsP  = rootsP[(abs(rootsP)<=1).nonzero()]
    # Sort roots with respect to its distance to the unit circle
    rootsP  = rootsP[(abs(abs(rootsP) - 1)).argsort()]
    return angle(rootsP[:p]) / 2 / pi
    
    

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
    for freq, amp in itertools.izip(freqs, amps):
        x += amp * exp(1j * 2 * pi * freq * n)
    awgn    = sqrt(noisePow/2) * randn(len(n)) + 1j * sqrt(noisePow/2) * randn(len(n))
    return x + awgn
    


if __name__ == '__main__':
    freqs       = [0.1, 0.18, 0.25]
    amps        = [1, 1, 1]
    noisePow    = 0.1
    N           = 10
    print('{} complex sinusoids are presented in additive white Gaussian noise.'.format(len(freqs)))
    print('Amplitudes of these sinusoids are:', amps)
    print('Frequencies of these sinusoids are:', freqs)
    print('Power of additive white Gaussian noise is', noisePow)
    x           = genTestSig(N, freqs, amps, noisePow)
    R           = Rx(x)
    print('Estimated frequencies (ESPRIT) are:    ', sort(LS_ESPRIT(R, len(freqs))))
    print('Estimated frequencies (root-MUSIC) are:', sort(root_MUSIC(R, len(freqs))))
    