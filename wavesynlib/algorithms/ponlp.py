# -*- coding: utf-8 -*-
"""
Created on Fri Mar 18 12:11:35 2016

@author: Feng-cong Li
"""
import numpy as np
from numpy import fft
from scipy.optimize import fmin_ncg

from wavesynlib.mathtools import Algorithm, Expression, Parameter


def objective(phi, Qr):
    N = len(phi)
    s = np.exp(1j*phi)
    Fs = fft.fft(s, 2*N)
    ac = fft.ifft(Fs * Fs.conj())
    return np.sum(np.abs(ac[Qr])**2)
    
    
def gradient(phi, Qr):
    N = len(phi)
    s = np.exp(1j*phi)
    Fs = fft.fft(s, 2*N)
    ac = fft.ifft(Fs * Fs.conj())
    grad = np.zeros((N,), dtype=np.complex128)
    for k in Qr:
        grad += ac[k].conj()*dak_dphi(k, s)
    return 2*grad.real
    
    
def hessian(phi, Qr):
    N = len(phi)
    s = np.exp(1j*phi)
    Fs = fft.fft(s, 2*N)
    ac = fft.ifft(Fs * Fs.conj())
    H = np.zeros((N, N), dtype=np.complex128)
    for k in Qr:
        d = dak_dphi(k, s)
        H += np.outer(d, d.conj()) + ac[k].conj()*d2ak_dphi2(k, s)
    return 2*H.real



def dak_dphi(k, s):
    t1 = 1j * s * np.hstack((np.zeros(k), s[:-k].conj()))    
    t2 = -1j * s.conj() * np.hstack((s[k:], np.zeros(k)))
    return t1 + t2
    
    
def d2ak_dphi2(k, s):
    diag = np.diag
    t1 = diag(s.conj()) @ diag(s[k:], k)
    t2 = -diag(s.conj()) @ diag(np.hstack((s[k:], np.zeros((k,)))))
    t3 = diag(s) @ diag(s[:-k], -k)
    t4 = -diag(s) @ diag(np.hstack((np.zeros((k,)), s[:-k])).conj())
    return t1 + t2 + t3 + t4
    
        
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
        phi = fmin_ncg(J, phi_init, fprime=dJ, fhess=d2J, avextol=1e-16, callback=callback)
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