from __future__ import print_function, division

from numpy import abs, isscalar, linalg, ndarray, mat, matrix, hstack
from numpy.linalg   import matrix_rank, svd
from collections import OrderedDict
import importlib

import abc

from wavesynlib.languagecenter.utils import eval_format, auto_subs
from wavesynlib.languagecenter.wavesynscript import Scripting, ModelNode, NodeDict
from wavesynlib.languagecenter import datatypes
from wavesynlib.toolwindows.basewindow import WindowComponent

import time
import thread
##########################Experimenting with multiprocessing###############################
import multiprocessing as mp
###########################################################################################


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
                if newOp.progress_checker(k, n, y, y_last):
                    break
                if newOp.iterThreshold > 0 and dist(y, y_last) <= newOp.iterThreshold:
                    break
                y_last  = y
            return y
        newOp.func  = fn
        return newOp
                


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



class ProgressChecker(object):
    def __init__(self, interval=1):
        self.__checkerChain = []
        self.interval=interval
        
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
        self.__progress_checker    = ProgressChecker()
    
    def __call__(self, *args, **kwargs):
        pass
    
    def presetParams(self, params):
        pass
    
    @property
    def progress_checker(self):
        return self.__progress_checker


class AlgorithmNode(ModelNode, WindowComponent):
    _xmlrpcexport_  = ['run']    
    
    class Meta(object):
        def __init__(self):
            self.name   = ''
            self.parameters      = OrderedDict()

    __parameters__      = None
    __name__            = None

    def __init__(self, module_name, class_name):
        super(AlgorithmNode, self).__init__()
        mod = importlib.import_module(module_name)
        algorithm = getattr(mod, class_name)()
        self.__cuda = True if hasattr(algorithm, '__CUDA__') and algorithm.__CUDA__ else False
        self.__meta = self.Meta()
        self.__meta.module_name  = module_name
        self.__meta.class_name   = class_name
        self.__meta.name    = algorithm.__name__
        self.__algorithm    = algorithm
        #self.__top_window    = None
        
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
    def need_cuda(self):
        return self.__cuda

    @property
    def meta(self):
        return self.__meta
        
    @property
    def progress_checker(self):
        return self.__algorithm.progress_checker

                    
    @Scripting.printable # To Do: Implement run in nonblocking mode. Add a new argument: on_finished. The callable object will be called when the procudure is finished. 
    def run(self, *args, **kwargs):
        result = self.__algorithm(*args, **kwargs)
        self.window_node.current_data  = result  
        
    @Scripting.printable
    def thread_run(self, on_finished, progress_bar, repeat_times, *args, **kwargs):
        from wavesynlib.toolwindows.progresswindow.dialog import Dialog

        def store_and_plot(result):
            window_node = self.window_node
            window_node.current_data = result            
            window_node.plot_current_data()            
        
        on_finished_proc = {
            'store and plot': store_and_plot
        }        
        
        if not callable(on_finished):
            on_finished = on_finished_proc[on_finished]

        root_node = self.root_node            
        
        algorithm_class = type(self.__algorithm)
        algorithm = algorithm_class()

        if progress_bar is None:
            pass
        elif progress_bar == 'dialog':
            dialog = Dialog(['Total progress:', 'Current progress:'], title=algorithm.__name__ + ' Progress')
            def default_progressbar(k, K, *args, **kwargs):
                progress = k / K * 100
                dialog.set_progress(index=1, progress=progress)
            algorithm.progress_checker.append(default_progressbar)
        else:
            raise NotImplementedError


        def run():
            t1 = time.clock()
            for n in range(repeat_times):
                result = algorithm(*args, **kwargs)
                slot = datatypes.CommandSlot(source='local', node_list=[on_finished], args=(result,))
                root_node.command_queue.put(slot)
                dialog.set_progress(index=0, progress=(n+1)/repeat_times * 100)
            delta_t = time.clock() - t1
            dialog.set_text(index=0, text=auto_subs('Finished. Total time consumption: $delta_t (s)'))
            
        thread.start_new_thread(run, ())
                                
    @property
    def node_path(self):
        if isinstance(self.parent_node, AlgorithmDict):
            return eval_format('{self.parent_node.node_path}["{self.meta.name}"]')
        else:
            return ModelNode.node_path
            
    def presetParams(self, params):
        self.__algorithm.presetParams(params)

##############################Experimenting with multiprocessing###################################
    @Scripting.printable
    def parallel_run_and_plot(self, all_args):     
        queue   = mp.Queue()
        for args, kwargs in all_args:
            mp.Process(target=parallelFunc, args=(type(self.__algorithm), queue, args, kwargs)).start()
        for k in range(len(all_args)):
            self.window_node.current_data  = queue.get()
            self.window_node.plot_current_data()
            
    @Scripting.printable
    def parallel_run(self, all_args):
        queue   = mp.Queue()
        retval  = {'process':[], 'queue':queue}
        for process_id, (args, kwargs) in enumerate(all_args):
            p   = mp.Process(target=parFunc, args=(type(self.__algorithm), process_id, queue, args, kwargs))
            retval['process'].append(p)
            p.start()            
        return retval
            
        

    
    
def parallelFunc(algorithm_class, queue, args, kwargs):
    result  = algorithm_class()(*args, **kwargs)
    queue.put(result)        
    
    
########################NEW#############################
def parFunc(algorithm_class, process_id, queue, args, kwargs):
    PROGRESS_ID     = 1
    RESULT_ID       = 0
    def progress_checker(k, K, y, *args, **kwargs):                
        queue.put((PROGRESS_ID, process_id, int(k / K * 100)))
    algorithm   = algorithm_class()
    algorithm.progress_checker.append(progress_checker)
    algorithm.progress_checker.interval  = 100
    result  = algorithm(*args, **kwargs)
    queue.put((RESULT_ID, result))
########################################################    
###################################################################################################


class AlgorithmDict(NodeDict, WindowComponent):
    def __init__(self, node_name=''):
        NodeDict.__init__(self, node_name=node_name)
                
    def __setitem__(self, key, val):
        if not isinstance(val, AlgorithmNode):
            raise TypeError, eval_format('{self.node_path} only accepts instance of Algorithm or of its subclasses.')
        if key != val.meta.name:
            raise ValueError, 'The key should be identical to the name of the algorithm.'
        NodeDict.__setitem__(self, key, val)
        
    def add(self, node):
        self[node['name']] = node