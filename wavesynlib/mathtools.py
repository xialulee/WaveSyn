from numpy import abs, isscalar, linalg, ndarray
from collections import OrderedDict

from common         import evalFmt
from objectmodel    import ModelNode, NodeDict
from application    import Scripting
from basewindow     import WindowNode


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


class Algorithm(ModelNode):
    class Meta(object):
        def __init__(self):
            self.name   = ''
            self.parameters      = OrderedDict()

    __parameters__      = None
    __name__            = None

    def __init__(self):
        super(Algorithm, self).__init__()
        self.__meta = self.Meta()
        self.__meta.name    = self.__name__
        self.__topWindow    = None
        
        if self.__parameters__:
            for item in self.__parameters__:
                self.__meta.parameters[item[0]]    = Parameter(*item)
        else:
            paramsnum   = self.__call__.func_code.co_argcount
            for param in self.__call__.func_code.co_varnames[1:paramsnum]:  
                self.__meta.parameters[param]   = Parameter(param, type='expression')

    def __call__(self, *args, **kwargs):
        pass

    @property
    def meta(self):
        return self.__meta

    @property        
    def topWindow(self):
        if self.__topWindow:
            return self.__topWindow
        else:
            node    = self
            while True:
                node    = node.parentNode
                if isinstance(node, WindowNode):
                    self.__topWindow    = node
                    return node
                    
    @Scripting.printable
    def run(self, *args, **kwargs):
        result  = self(*args, **kwargs)
        self.topWindow.currentData  = result    
        
        
    @property
    def nodePath(self):
        if isinstance(self.parentNode, AlgorithmDict):
            return evalFmt('{self.parentNode.nodePath}["{self.meta.name}"]')
        else:
            return ModelNode.nodePath        



class AlgorithmDict(NodeDict):
    def __init__(self, nodeName=''):
        NodeDict.__init__(self, nodeName=nodeName)
                
    def __setitem__(self, key, val):
        if not isinstance(val, Algorithm):
            raise TypeError, evalFmt('{self.nodePath} only accepts instance of Algorithm or of its subclasses.')
        if key != val.meta.name:
            raise ValueError, 'The key should be identical to the name of the algorithm.'
        NodeDict.__setitem__(self, key, val)
        
    def add(self, node):
        self[node.meta.name] = node