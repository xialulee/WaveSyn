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

from wavesynlib.formulae.noise import complex_gaussian
    
from numpy import (
    array, arange, correlate, roots, trace, atleast_1d, exp, 
    zeros, eye, unravel_index, einsum, full, 
    c_,
    inf, angle, pi as π
)
from numpy.linalg import eigh, eigvals, pinv, lstsq, det
from itertools import combinations
from .autocorrmtx import Rx, autocorrelate

_2π = 2 * π



def LS_ESPRIT(Rx, p):
    """Estimate signal frequencies using LS-ESPRIT algorithm
Rx: autocorrelation matrix of signal;
p:   number of complex sinusoids;
return value: normalized frequencies."""
    p, N = int(p), Rx.shape[0]
    D, U = eigh(Rx)
#    Obtain signal subspace from U
#    Unlike numpy.linalg.svd, 
#    the eigenvalue and the corresponding eigenvectors 
#    calculated by eigh are in ascending order. 
    U_s = U[:, N-p:]
    U_0 = U_s[:-1, :]
    U_1 = U_s[1:, :]
    U1_U0 = lstsq(U_1, U_0, rcond=None)[0]
    return -(angle(eigvals(U1_U0)) / _2π)



def root_MUSIC(Rx, p):
    """Estimate signal frequencies using root-MUSIC algorithm
Rx: auto-correlation matrix of signal;
p:  number of complex sinusoids;
return value: normalized frequencies."""
    p, N = int(p), Rx.shape[0]
    # Eigenvalue in ascending order.
    D, U = eigh(Rx)
    # An orth base of the noise subspace.
    U_n = U[:, :N-p]
    P = sum(autocorrelate(u) for u in U_n.T)
    roots_P = roots(P)
    # Remove all the roots outside the unit circle.
    roots_P = roots_P[(abs(roots_P) <= 1).nonzero()]
    # Sort the roots with respect to its distance to the unit circle.
    roots_P = roots_P[abs(roots_P).argsort()]
    return angle(roots_P[-1:-p-1:-1]) / _2π



def MLE(Rx, p, freq_samps=arange(0, 1, 0.01)):
    p, N, Nf = int(p), Rx.shape[0], len(freq_samps)
    I = eye(N)

    def Es(freqs):
        """Create a steering matrix."""
        freqs = atleast_1d(freqs)
        n = c_[:N]
        ω = _2π * freqs
        return exp(1j * n * ω)
    F = full([Nf] * p, inf)
    for idx in combinations(range(Nf), p):
        A = Es(freq_samps[array(idx)])
        Aᴴ = A.T.conj()
        pinv_A = pinv(A)
        pinv_A_H = pinv_A.T.conj()
        P_A = A @ pinv_A
        P_N = eye(P_A.shape[0]) - P_A
        σ_sq = (einsum('ij,ji->', P_N, Rx) / (N - p)).real
        σ_sq_I = σ_sq * I
        Rs = pinv_A @ (Rx - σ_sq_I) @ pinv_A_H
        F[idx] = det(A @ Rs @ Aᴴ + σ_sq_I).real
    sub = array(unravel_index(F.argmin(), F.shape))
    return freq_samps[sub]
    
    

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
    print('Estimated frequencies (MLE) are:       ', sort(MLE(R, len(freqs))))
    