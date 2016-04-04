# -*- coding: utf-8 -*-
"""
Created on Wed Dec 09 11:05:00 2015

@author: Feng-cong Li
"""
from __future__ import division, print_function


def Q(nu, lambda_, x, epsilon=1e-5):
    '''
This function is translated from a Matlab function originally written by S.M. Kay, see [1].
Q computes the right-tail probability of a central or noncentral chi-squared PDF.

Input Parameters:

    nu      = Degrees of Freedom (DoF)
    lambda_ = Noncentrality parameter (0 for central chi-square)
    x       = Random variable
    epsilon = maximum allowable error (should be a small number such as 1e-5) due to the truncation of the infinite sum
    
[1] S. Kay, Fundamental of statistical signal processing, Vol. 2: detection theory, Prentice-Hall, Upper Saddle River, NJ, 1998.    
    '''
    from math import erfc, exp, factorial, pi, sqrt
    normRT = lambda x: 0.5*erfc(x/sqrt(2))
    t = exp(lambda_ / 2.0) * (1 - epsilon)
    sum_ = 1
    M = 0
    while sum_ < t:
        M += 1
        sum_ += ((lambda_ / 2.0)**M) / factorial(M)
        
    if nu / 2 - nu // 2: # nu is odd
        P = 2 * normRT(sqrt(x))
        g = Q2p = sqrt(2*x/pi) * exp(-x/2)
        if nu > 1:
            for m in range(5, nu+1, 2):
                g *= x / (m-2)
                Q2p += g
            P += exp(-lambda_ / 2) * Q2p
            for k in range(1, M+1):
                m = nu + 2 * k
                g *= x / (m - 2)
                Q2p += g
                arg = (exp(-lambda_/2) * (lambda_/2)**k) / factorial(k)
                P += arg * Q2p
        else: # nu == 1
            P += exp(-lambda_ / 2) * (lambda_ / 2) * Q2p
            for k in range(2, M+1):
                m = nu + 2*k
                g *= x / (m-2)
                Q2p += g
                arg = (exp(-lambda_ / 2) * (lambda_/2)**k) / factorial(k)
                P += arg * Q2p
    else: # nu is even
        g = Q2 = exp(-x/2)
        for m in range(4, nu+1, 2):
            g *= x / (m-2)
            Q2 += g
        P = exp(-lambda_/2) * Q2
        for k in range(1, M+1):
            m = nu + 2*k
            g *= x / (m-2)
            Q2 += g
            arg = (exp(-lambda_/2) * (lambda_/2)**k) / factorial(k)
            P += arg * Q2
    return P
    
    
def thresholdNP(Pfa, N, comp=False, epsilon=1e-5, interval=(0, 1e24)):
    '''
thresholdNP calculates the threshold of the energy detector with the given false alarm probability Pfa.
Pfa:        False Alarm Probability;
N:          The number of the real/complex Gaussian variables.
epsilon:    Minimum allowable error of chisquare.Q
interval:   The interval where the threshold is found. 

Signal model:
The detection statistic of the energy detector is ||x||**2
H0: x = w
H1: x = s + w
If comp = False:
    The additive Gaussian noise vector w~N(0, I) where I is a N-by-N identity matrix.
If comp = True:
    The additive Gaussian noise vector w~CN(0, I) where I is a N-by-N identity matrix.
    '''
    from scipy.optimize import brentq
    f = lambda x: Q(N*2 if comp else N, 0, x, epsilon) - Pfa
    return brentq(f, *interval) / (2 if comp else 1)

    

if __name__ == '__main__':
    import numpy as np
    from numpy import linalg
    print('Test chisquare.Q:')
    print('(nu=1, lambda_=2, x=0.5, epsilon=0.0001) should produce 0.7772.')
    print('Q(1, 2, 0.5, 0.0001) = {0}'.format(Q(1, 2, 0.5, 0.0001)))
    print()
    print('(nu=5, lambda_=6, x=10,  epsilon=0.0001) should produce 0.5063.')
    print('Q(5, 6, 10, 0.0001) = {0}'.format(Q(5, 6, 10, 0.0001)))
    print()
    print('(nu=8, lambda_=10, x=15, epsilon=0.0001) should produce 0.6161.')
    print('Q(8, 10, 15, 0.0001) = {0}'.format(Q(8, 10, 15, 0.0001)))
    print()
    
    print('Test chisquare.thresholdNP:')
    Pfa     = 1e-4
    dim     = 4
    print('(Pfa={0}, N={1}) for complex additive noise w~CN(0, I)'.format(Pfa, dim))    
    comp    = True
    threshold = thresholdNP(Pfa, dim, comp=comp)
    event = 0
    testNum = 1e6
    for k in range(10**6):
        if linalg.norm(np.sqrt(0.5) * (np.random.randn(4, 1) + 1j * np.random.randn(4, 1))) ** 2 > threshold:
            event += 1
    print('Simulation results: Pfa = {0}'.format(event / testNum))    