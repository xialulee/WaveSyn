# -*- coding: utf-8 -*-
"""
Created on Wed Apr 30 22:19:30 2014

@author: Tao Zhang, Feng-cong Li (xialulee@sina.com)
"""

from numpy import exp, kron, mat, pi, r_, real, sin, vstack, zeros, ones, diag
import cvxpy as cp
from collections.abc import Iterable
from abc import ABCMeta, abstractproperty

class BasePattern(metaclass=ABCMeta):
    @abstractproperty    
    def samplesMagnitude(self):
        raise NotImplementedError
        
    @abstractproperty        
    def samplesAngle(self):
        raise NotImplementedError
    
    @classmethod
    def __subclasshook__(cls, C):
        if cls is BasePattern:
            if hasattr(C, 'samplesMagnitude') and hasattr(C, 'samplesAngle'):
                return True
        return NotImplemented


class PiecewisePattern(BasePattern):
    '''Create and maintain a piecewise beam pattern.
center: the centers of the beams (in degree);
width:  the width of the beams (in degree).'''    
    def __init__(self, samplesAngle=None, beamsAngle=None, beamsWidth=None):
        self.__samplesAngle = []
        self.__samplesMagnitude = []
        if samplesAngle is not None and beamsAngle is not None and beamsWidth is not None:
            self.createPiecewisePattern(samplesAngle, beamsAngle, beamsWidth)

    def createPiecewisePattern(self, samplesAngle, beamsAngle, beamsWidth):
        mag = zeros(len(samplesAngle))  
        for k in range(len(beamsAngle)):
            for index, theta in enumerate(samplesAngle):
                if abs(theta - beamsAngle[k]) < beamsWidth[k]/2.0:
                    mag[index]    = 1
        self.__samplesAngle = samplesAngle
        self.__samplesMagnitude = mag
        return self
        
    @property
    def samplesAngle(self):
        return self.__samplesAngle
        
    @property
    def samplesMagnitude(self):
        return self.__samplesMagnitude

def matJ(M):
    'Return a complex M^2 * M^2 permutaion matrix J which satisfies vec(R) == Jr.'
    ret = zeros((M**2, M**2), complex)
    
    k   = 0
    addr_table  = {}
    for q in range(M):
        for p in range(q, M):
            addr_table[(p,q)] = k
            k += 1 if p==q else 2
    
    for q in range(M):
        for p in range(M):
            row = q*M + p
            if p == q:
                ret[row, addr_table[(p,q)]]   = 1
            else:
                addr    = addr_table[(p,q)] if p > q else addr_table[(q,p)]
                ret[row, addr]    = 1
                ret[row, addr+1]  = 1j if p > q else -1j
    return mat(ret)
    
    
def matA(M, angles):
    'The steering matrix.'
    ret = zeros((M, len(angles)), complex)
    for col, theta in enumerate(angles):
        ret[:, col] = exp(1j * pi * r_[0:M] * \
        sin(pi * theta / 180.))
    return mat(ret)
    

    
def matG(M, angles, magnitude):
    G1  = zeros((M**2+1, M**2+1))
    A   = matA(M, angles)
    J   = matJ(M)
    for index, theta in enumerate(angles):
        g   = -(kron(A[:,index].T, A[:,index].H) @ J).T
        t   = vstack((magnitude[index], g))
        G1  += real(t @ t.T)
    G1  = 1.0/len(angles) * G1
    G1  = real(G1)
    return G1
    
                
              
def corrmtx2pattern(R, angles):
    M   = R.shape[0]
    ret = zeros(len(angles))    
    A   = matA(M, angles)
    for k in range(len(angles)):
        ret[k]  = real((A[:, k].H * R * A[:, k])[0,0])
    ret /= max(ret)
    return ret

class Problem(object):
    def __init__(self):
        self.__M    = None
        self.__idealPattern   = None
        self.__Gamma    = None
    
    @property
    def M(self):
        '''The number of the array elements.'''
        return self.__M 

    @M.setter
    def M(self, val):
        val = int(val)
        if val != self.__M:
            self.__M    = val            
            
    @property
    def idealPattern(self):
        return self.__idealPattern
        
    @idealPattern.setter
    def idealPattern(self, val):
        if not isinstance(val, BasePattern):
            raise TypeError('idealPattern should assign to an instance of a derived class of BasePattern.')
        if (not isinstance(val.samplesAngle, Iterable)) or\
                (not isinstance(val.samplesMagnitude, Iterable)):
            raise TypeError('angle and magnitude of idealPattern should be iterable.')
        if len(val.samplesAngle) != len(val.samplesMagnitude):
            raise Exception('len(idealPattern.angle) should equal len(idealPattern.magnitude).')
        Gamma   = matG(self.M, val.samplesAngle, val.samplesMagnitude)
        self.__Gamma    = Gamma 
        self.__idealPattern = val
            
    def solve(self, *args, **kwargs):
        self.__setup()
        self.__problem.solve(*args, **kwargs)  
        return self.__R.value
        

    def __setup(self):  
        M = self.__M     
        J = matJ(M)
        R = cp.Variable((M, M), hermitian=True)
        rho = cp.Variable((1+M**2,))
        alpha = rho[0]
        r = rho[1:]
                
        objective = cp.Minimize(cp.quad_form(rho, self.__Gamma))
        
        constraints = [
            R >> 0,
            alpha >= 0,
            cp.vec(R) == J@r,
            cp.diag(cp.real(R)) == 1]         
        
        problem = cp.Problem(objective, constraints)
        self.__problem  = problem
        self.__R = R





if __name__ == '__main__':
    from pylab import *
    def test():
        M   = 10                
        angles  = r_[-90:90.1:0.1]
        idealp = PiecewisePattern(angles, [40], [20])        
        
        problem = Problem()
        problem.M = M
        problem.idealPattern = idealp
        R = problem.solve(verbose=True)    
        print(diag(R))
        pattern = corrmtx2pattern(R, angles)
        plot(angles, pattern)
#        hold(True)
        plot(angles, idealp.samplesMagnitude, 'r')  
        show()    
    test()
