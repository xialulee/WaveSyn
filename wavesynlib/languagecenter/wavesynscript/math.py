# -*- coding: utf-8 -*-
"""
Created on Tue May 02 15:36:34 2017

@author: Feng-cong Li
"""
from __future__ import print_function, division, unicode_literals

import abc
from numpy import abs, isscalar, linalg, ndarray, mat, matrix, hstack
from numpy.linalg   import matrix_rank, svd



class Operator(object):
    def __init__(self, func=None):
        '''init'''
        self.__f    = func
        self.iterThreshold  = 0


    @property
    def func(self):
        return self.__f

        
    @func.setter
    def func(self, f):
        if not callable(f):
            raise TypeError('f must be a callable object.')
        self.__f    = f

        
    def __call__(self, *args):
        '''Evaluate'''
        return self.__f(*args)


    def comp(self, g):
        '''Operator composition'''
        return Operator(lambda *args: self.__f(g.func(*args)))


    def __mul__(self, g):
        '''Operator composition
Though it is not appropriate to use * to denote operator composition,
the code can be simplified a lot.
'''
        return self.comp(g)


    def __pow__(self, n, dist=None):
        '''The power of the operator.
(f.pow(3))(x) == f(f(f(x))).        
'''
        if not dist:
            def dist(x, y):
                if isscalar(x) and isscalar(y):
                    return abs(x-y)
                elif isinstance(x, ndarray):
                    return linalg.norm(x-y)
                else:
                    pass # throw an exception
            
        f   = self.__f
        newOp   = Operator()
        def fn(x):
            y_last  = f(x)
            for k in range(1, n):
                y   = f(y_last)
                if newOp.progress_checker(k, n, y, y_last):
                    break
                if newOp.iterThreshold > 0 and dist(y, y_last) <= newOp.iterThreshold:
                    break
                y_last  = y
            return y
        newOp.func  = fn
        return newOp
        
        
        
class SpecialMatrix(Operator):
    def __mul__(self, g):
        if isinstance(g, (ndarray, mat)):
            pass
        else:
            super(SpecialMatrix).__mul__(g)
            
            
    def __rmul__(self, g):
        if isinstance(g, (ndarray, mat)):
            pass
        else:
            g * self
                


class SetWithProjector(object):
    __metaclass__   = abc.ABCMeta

    
    @abc.abstractproperty
    def projector(self):
        return NotImplemented

        
    @abc.abstractmethod
    def __contains__(self, x):
        return NotImplemented

        
    @classmethod
    def __subclasshook__(cls, C):
        if cls is SetWithProjector:
            if hasattr(C, 'projector') and hasattr(C, '__contains__'):
                return True
        return NotImplemented    
        

        
class Col(SetWithProjector):    
    '''A data structure represents the column space (range space) defined by a matrix.'''
    def __init__(self, A):
        if not isinstance(A, matrix):
            A   = mat(A)
        self.__A    = A
        self.__proj = None
        U, S, VH    = svd(A)
        rank        = matrix_rank(A)
        self.__rank = rank
        B           = U[:, 0:rank]
        self.__basis    = B
        self.__proj = Operator(func=lambda x: B * B.H*x)

            
    @property    
    def projector(self):
        '''return the projector of the column space.'''
        return self.__proj

        
    @property
    def orth(self):
        '''return the an orthonormal basis for this column space.
For a matrix A, "Col(A).orth" is equivalent to the matlab expression "orth(A)."
'''
        return self.__basis

        
    def __contains__(self, x):
        '''If column vector x lies in Col(A), then __contains__ return True.'''
        C   = hstack((self.__A, x))
        return matrix_rank(C) == self.__rank