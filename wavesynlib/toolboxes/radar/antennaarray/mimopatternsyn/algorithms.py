# -*- coding: utf-8 -*-
"""
Created on Wed Apr 30 22:19:30 2014

@author: Tao Zhang, Feng-cong Li (xialulee@sina.com)
"""

from numpy import exp, kron, mat, pi, r_, real, sin, vstack, zeros, ones, diag
import cvxpy as cp
from collections.abc import Iterable
from abc import ABCMeta, abstractproperty

from .pattern2corrmtx import make_quadform_matrix, corrmtx2pattern, make_problem



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



class Problem(object):
    def __init__(self):
        self.__M    = None
        self.__idealPattern   = None
        self.__Gamma    = None
        self.__problem = None
        self.__R = None
    
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
        Gamma   = make_quadform_matrix(self.M, (val.samplesAngle, val.samplesMagnitude))
        self.__Gamma    = Gamma 
        self.__idealPattern = val
            
    def solve(self, *args, **kwargs):
        self.__setup()
        self.__problem.solve(*args, **kwargs)  
        return self.__R.value
        

    def __setup(self):  
        M = self.__M
        Gamma = self.__Gamma
        problem, R = make_problem(M, Gamma)
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
