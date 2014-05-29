from numpy import abs, isscalar, linalg, ndarray
from collections import OrderedDict

from common         import evalFmt, autoSubs
from objectmodel    import ModelNode, NodeDict
from application    import Scripting
from basewindow     import WindowComponent


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
            raise TypeError, 'f must be a callable object.'
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
                if newOp.progressChecker(k, n, y, y_last):
                    break
                if newOp.iterThreshold > 0 and dist(y, y_last) <= newOp.iterThreshold:
                    break
                y_last  = y
            return y
        newOp.func  = fn
        return newOp
                


class ProgressChecker(object):
    def __init__(self, interval=1):
        self.__checkerChain = []
        
    def append(self, checker):
        if not callable(checker):
            raise TypeError, 'Checker must be callable.'
        self.__checkerChain.append(checker)
        
    def remove(self, checker):
        self.__checkerChain.remove(checker)
        
    def __call__(self, k, K, x, *args, **kwargs):
        '''k:   the number of the current iteration;
K:  the maximum iteration number;
x:  the current optimization variable;
args:   the extra position paramters;
kwargs  the extra key paramters.        
'''
        exitIter    = False
        if k == K:
            exitIter    = True
            return exitIter
        if k % self.interval != 0:
            exitIter    = False
            return exitIter
        for checker in self.__checkerChain:
            ret = checker(k, K, x, *args, **kwargs)
            if ret:
                exitIter    = ret
        return exitIter


class Parameter(object):
    def __init__(self, name='', type='', shortdesc='', longdesc=''):
        self.name   = name
        self.type   = type
        self.shortdesc  = shortdesc
        self.longdesc   = longdesc


class Algorithm(object):
    __parameters__  = None
    __name__        = None
    
    def __init__(self):
        self.__progressChecker    = ProgressChecker()
    
    def __call__(self, *args, **kwargs):
        pass
    
    @property
    def progressChecker(self):
        return self.__progressChecker


class AlgorithmNode(ModelNode, WindowComponent):
    class Meta(object):
        def __init__(self):
            self.name   = ''
            self.parameters      = OrderedDict()

    __parameters__      = None
    __name__            = None

    def __init__(self, moduleName, className):
        super(AlgorithmNode, self).__init__()
        mod         = __import__(autoSubs('algorithms.$moduleName'), globals(), locals(), [className], -1)
        algorithm   = getattr(mod, className)()
        self.__meta = self.Meta()
        self.__meta.moduleName  = moduleName
        self.__meta.className   = className
        self.__meta.name    = algorithm.__name__
        self.__algorithm    = algorithm
        self.__topWindow    = None
        
        if algorithm.__parameters__:
            for item in algorithm.__parameters__:
                self.__meta.parameters[item[0]]    = Parameter(*item)
        else:
            paramsnum   = algorithm.__call__.func_code.co_argcount
            for param in algorithm.__call__.func_code.co_varnames[1:paramsnum]:  
                self.__meta.parameters[param]   = Parameter(param, type='expression')

    def __getitem__(self, key):
        return getattr(self.__meta, key)

    @property
    def meta(self):
        return self.__meta
        
    @property
    def progressChecker(self):
        return self.__algorithm.progressChecker

                    
    @Scripting.printable
    def run(self, *args, **kwargs):
        result  = self.__algorithm(*args, **kwargs)
        self.topWindow.currentData  = result    
        
        
    @property
    def nodePath(self):
        if isinstance(self.parentNode, AlgorithmDict):
            return evalFmt('{self.parentNode.nodePath}["{self.meta.name}"]')
        else:
            return ModelNode.nodePath        



class AlgorithmDict(NodeDict, WindowComponent):
    def __init__(self, nodeName=''):
        NodeDict.__init__(self, nodeName=nodeName)
                
    def __setitem__(self, key, val):
        if not isinstance(val, AlgorithmNode):
            raise TypeError, evalFmt('{self.nodePath} only accepts instance of Algorithm or of its subclasses.')
        if key != val.meta.name:
            raise ValueError, 'The key should be identical to the name of the algorithm.'
        NodeDict.__setitem__(self, key, val)
        
    def add(self, node):
        self[node['name']] = node