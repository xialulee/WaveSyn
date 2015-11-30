# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 16:53:10 2015

@author: Feng-cong Li
"""
from scipy.misc import comb, factorial
from math import exp

def partition(V, N): # get N integers of which the summation equals V
    if V < 0:
        return
    else:
        if N == 0:
            if V != 0:
                return
            else:
                yield []
        else:
            for i in range(V+1):
                for j in partition(V-i, N-1):
                    j.insert(0, i)
                    yield j
        
def Psi(k, l, r, sigma2):
    M = len(r)
    result = 0
    for i in partition(l, M-1):
        i.insert(k, 0)
        temp = 1
        for j in range(M):
            if j == k:
                continue
            temp *= comb(i[j]+r[j]-1, i[j])
            temp *= (1./sigma2[j] - 1./sigma2[k]) ** (-r[j]-i[j])
        result += temp
    result = (-1) ** (r[k]-1)
    return result
    
 
# important! No correct   
def ccslcpdf(x, r, sigma2): # complex chi-square linear combination probability density function
    M = len(r)
    result = 1
    for m in range(M):
        temp0 = 0
        for k in range(M):
            temp1 = 0
            for l in range(r[k]):
                temp2  = Psi(k, l, r, sigma2)
                temp2 /= factorial(r[k] - (l + 1))
                temp2 *= (-x)**(r[k]- (l + 1)) * exp(-x/sigma2[k])
                temp1 += temp2
            temp0 += temp1
        result *= temp0 / sigma2[m]**r[m]
    return result



if __name__ == '__main__':
    import numpy as np
    import pylab    
    DoF         = [3, 1]
    C           = [8, 2]
    Nsamples    = 4096
    Samples     = np.zeros((sum(DoF)*2, Nsamples))
    startRow    = 0
    for idx in range(len(DoF)):
        sigma = np.sqrt(C[idx]/2.)
        Samples[startRow:(startRow+DoF[idx]*2), :] = sigma * np.random.randn(DoF[idx]*2, Nsamples)
        startRow += 2*DoF[idx]
    Samples = Samples ** 2
    Samples = np.sum(Samples, axis=0)
    hist, edges = np.histogram(Samples, bins=50, density=True)
    centers = (edges + (edges[1] - edges[0]) / 2.0)[:-1]
    pdf = [ccslcpdf(center, DoF, C) for center in centers]    
    pylab.plot(centers, hist)
    pylab.hold('on')
    pylab.plot(centers, pdf, 'r')
    pylab.show()
        