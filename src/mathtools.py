from numpy import abs, isscalar, linalg, ndarray
from collections import OrderedDict




class Operator(object):
    def __init__(self, func):
        '''init'''
        self.__f    = func
        self.exitcond   = {}

    @property
    def func(self):
        return self.__f
        
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

    def __pow__(self, n, dist=None, thres=0):
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
        def fn(x):
            y_last  = f(x)
            for k in range(1, n):
                y   = f(y_last)
                if self.exitcond and k % self.exitcond['interval']==0 \
                   and self.exitcond['func'](k, n, y, y_last):
                    break
                y_last  = y
            return y
        return Operator(fn)
                



class Parameter(object):
    def __init__(self, name='', type='', shortdesc='', longdesc=''):
        self.name   = name
        self.type   = type
        self.shortdesc  = shortdesc
        self.longdesc   = longdesc


class Algorithm(object):
    class Meta(object):
        def __init__(self):
            self.algoname   = ''
            self.params = OrderedDict()

    __params__  = None
    __algoname__    = None

    def __init__(self):
        self.__meta = self.Meta()
        self.__meta.algoname    = self.__algoname__
        
        if self.__params__:
            for item in self.__params__:
                self.__meta.params[item[0]]    = Parameter(*item)
        else:
            paramsnum   = self.__call__.func_code.co_argcount
            for param in self.__call__.func_code.co_varnames[1:paramsnum]:  
                self.__meta.params[param]   = Parameter(param, type='expression')

    @property
    def meta(self):
        return self.__meta

    def __call__(self):
        pass



