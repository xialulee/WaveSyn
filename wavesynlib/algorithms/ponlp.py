# -*- coding: utf-8 -*-
"""
Created on Fri Mar 18 12:11:35 2016

@author: Feng-cong Li
"""
import numpy as np
from numpy.fft import fft, ifft
from scipy.optimize import fmin_ncg
from numpy import diag, exp, outer, roll 

from wavesynlib.mathtools import Algorithm, Expression, Parameter



def U(n, x):
    """The upper shift operator. See Eq.8 in [1]."""
    n = -n
    if n == 0:
        x = x.copy()
    else:
        if n > 0:
            x = roll(x, n)
            x[:n] = 0
        else:
            if n < 0:
                x = x.copy()
                x[0:-n] = 0
                x = roll(x, n)
    return x


def abs_square(x):
    return x.real**2 + x.imag**2


def autocorr(x):
    N = len(x)
    F = fft(x, n=2*N)
    return ifft(F * F.conj())


def objective(phase_vec, select_vec):
    return sum(abs_square(autocorr(exp(1j*phase_vec))[select_vec]))


def dan_dɸ(𝐬, n):
    sc = s.conj()
    # See Eq.44 in [1]
    t1 =  1j * s  * U(-n, sc)
    t2 = -1j * sc * U( n, s)
    return t1 + t2


def gradient(phase_vec, Q):
    s = exp(1j * phase_vec)
    a = autocorr(s)
    # See Eq.43 in [1]
    grad = sum(
        a[k].conj() * dan_dɸ(s, n=k) for k in Q
    )
    return 2 * grad.real


def d2an_dɸdɸ(s, n):
    Diag_s = diag(s)
    Diag_sc = diag(s.conj())
    U_Diag_s = diag(s[n:], n)
    Diag_U_s = diag(U(n, s))
    UT_Diag_sc = diag(s[0:-n], -n).conj()
    Diag_UT_sc = diag(U(-n, s).conj())
    # See Eq.49 in [1]
    t1 = Diag_sc @ U_Diag_s
    t2 = -Diag_sc @ Diag_U_s
    t3 = Diag_s @ UT_Diag_sc
    t4 = -Diag_s @ Diag_UT_sc
    return t1 + t2 + t3 + t4


def hessian(phase_vec, select_vec):
    s = exp(1j * phase_vec)
    a = autocorr(s)

    H = 0
    for k in select_vec:
        dak_dɸ = dan_dɸ(s, n=k)
        # See Eq.48 in [1].
        H += \
            a[k].conj() * d2an_dɸdɸ(s, n=k) +\
            outer(dak_dɸ, dak_dɸ.conj())
        
    return 2 * H.real

        
class PONLP(Algorithm):
    __name__ = 'PONLP'
    def __init__(self):
        super().__init__()

        
    def initpoint(self, N):
        return np.exp(1j * 2 * np.pi * np.random.rand(N))
        

    def __call__(self, 
                 N: Parameter(int, 'Sequence Length.'), 
                 Qr: Parameter(Expression, 'The interval in which correlation sidelobes are suppressed.'), 
                 tol: Parameter(float, 'Tolerance.')):
        s_init = self.initpoint(N)
        phi_init = np.angle(s_init)
        if not isinstance(Qr, np.ndarray):
            Qr = np.array(Qr)
        J = lambda phi: objective(phi, Qr)
        dJ = lambda phi: gradient(phi, Qr)
        d2J = lambda phi: hessian(phi, Qr)
        k_iter = [0]
        print('k\tJ(\u03c6)')
        def callback(phi):
            k_iter[0] += 1
            print(f'{k_iter[0]}\t{J(phi)}')        
        phi = fmin_ncg(J, phi_init, 
            fprime=dJ, 
            fhess=d2J, 
            avextol=1e-16, 
            callback=callback)
        return np.exp(1j*phi)
        

def test():
    N = 10
    Qr = np.r_[1:3]
    init = np.ones(N)
    J = lambda phi: objective(phi, Qr)
    dJ = lambda phi: gradient(phi, Qr)
    d2J = lambda phi: hessian(phi, Qr)
    def callback(phi):
        print(J(phi))
    phi = fmin_ncg(J, init, fprime=dJ, fhess=d2J, avextol=1e-16, callback=callback)
    return np.exp(1j*phi)
    
        
if __name__ == '__main__':
    test()