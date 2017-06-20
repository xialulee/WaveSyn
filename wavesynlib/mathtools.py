from __future__ import print_function, division

from collections import OrderedDict, Iterable
import importlib


from wavesynlib.languagecenter.utils import eval_format, auto_subs
from wavesynlib.languagecenter.wavesynscript import ScriptCode, Scripting, ModelNode, NodeDict
from wavesynlib.languagecenter import datatypes
from wavesynlib.toolwindows.tkbasewindow import WindowComponent

import time
import multiprocessing as mp



class ProgressChecker(object):
    def __init__(self, interval=1):
        self.__checkerChain = []
        self.interval=interval

        
    def append(self, checker):
        if not callable(checker):
            raise TypeError('Checker must be callable.')
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
        self.__cuda_worker = None

    
    def __call__(self, *args, **kwargs):
        pass

    
    def presetParams(self, params):
        pass

    
    @property
    def progress_checker(self):
        return self.__progress_checker
        
        
    @property
    def cuda_worker(self):
        return self.__cuda_worker
        
        
    @cuda_worker.setter
    def cuda_worker(self, worker):
        self.__cuda_worker = worker
        
        
        
class DataContainer(object):
    pass



class AlgorithmNode(ModelNode):
    _xmlrpcexport_  = ['run']    

    
    class Meta(object):
        def __init__(self):
            self.name   = ''
            self.parameters = OrderedDict()


    __parameters__ = None
    __name__ = None


    def __init__(self, module_name, class_name):
        super(AlgorithmNode, self).__init__()
        if isinstance(module_name, bytes):
            module_name = module_name.decode('utf-8')
        if isinstance(class_name, bytes):
            class_name = class_name.decode('utf-8')
        mod = importlib.import_module(module_name)
        algorithm = getattr(mod, class_name)()
        self.__cuda = True if hasattr(algorithm, '__CUDA__') and algorithm.__CUDA__ else False
        self.__meta = self.Meta()
        self.__meta.module = mod
        self.__meta.module_name = module_name
        self.__meta.class_name = class_name
        self.__meta.name    = algorithm.__name__
        self.__algorithm    = algorithm
        
        if algorithm.__parameters__:
            for item in algorithm.__parameters__:
                self.__meta.parameters[item[0]]    = Parameter(*item)
        else:
            paramsnum   = algorithm.__call__.func_code.co_argcount
            for param in algorithm.__call__.func_code.co_varnames[1:paramsnum]:  
                self.__meta.parameters[param]   = Parameter(param, type='expression')
                
                
    @property
    def data_container(self):
        node = self
        while True:
            node = node.parent_node
            if isinstance(node, DataContainer):
                return node 


    def on_connect(self):
        super(AlgorithmNode, self).on_connect()
        if self.need_cuda:
            self.__algorithm.cuda_worker = self.root_node.interfaces.gpu.cuda_worker
            
    
    @Scripting.printable       
    def reload_algorithm(self):
        reload(self.__meta.module)

                           
    def __getitem__(self, key):
        return getattr(self.__meta, key)
        
        
    @property
    def algorithm_object(self):
        return self.__algorithm


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
        self.data_container.current_data  = result  
        
        
    def data_container_exec(self, command, **kwargs):
        {
            'store': lambda: setattr(self.data_container, 'current_data', kwargs['data']),
            'plot': lambda: self.data_container.plot(kwargs['data'])
        }[command]()


    def _data_container_command_seq_exec(self, seq, data):
        if not isinstance(seq, Iterable):
            seq = [seq]
        for command in seq:
            if not callable(command):
                self.data_container_exec(command, data=data)
            else:
                command(data)

        
    @Scripting.printable
    def thread_run(self, on_finished, progress_indicator, repeat_times, *args, **kwargs):
        from wavesynlib.toolwindows.progresswindow.dialog import Dialog
                    
        root_node = self.root_node            
        
        algorithm_class = type(self.__algorithm)
        algorithm = algorithm_class()

        if progress_indicator is None:
            pass
        elif progress_indicator == 'progress_dialog':
            dialog = Dialog(['Total progress:', 'Current progress:'], title=algorithm.__name__ + ' Progress')
            def default_progressbar(k, K, *args, **kwargs):
                progress = k / K * 100
                dialog.set_progress(index=1, progress=progress)
                
            algorithm.progress_checker.append(default_progressbar)
        else:
            raise NotImplementedError
            
        if self.need_cuda:
            # Get the CUDA worker ready
            worker = root_node.interfaces.gpu.cuda_worker
            algorithm.cuda_worker = worker
            worker.activate()
            
            def run_algorithm(*args, **kwargs):
                worker.message_in.put({'command':'call', 'callable object':algorithm, 'args':args, 'kwargs':kwargs})
                return worker.message_out.get()['return value']
        else:
            run_algorithm = algorithm

        @root_node.thread_manager.new_thread_do
        def run():
            t1 = time.clock()

            for n in range(repeat_times):
                result = run_algorithm(*args, **kwargs)
                root_node.thread_manager.main_thread_do(block=False)(
                    lambda data=result: \
                        self._data_container_command_seq_exec(on_finished, data=data)
                )
                
                dialog.set_progress(index=0, progress=(n+1)/repeat_times * 100)
                    
            delta_t = time.clock() - t1
            dialog.set_text(index=0, text=auto_subs('Finished. Total time consumption: $delta_t (s)'))
            
            
    @Scripting.printable
    def process_run(self, on_finished, progress_indicator, repeat_times, *args, **kwargs):
        from wavesynlib.toolwindows.progresswindow.dialog import Dialog
        
        root_node = self.root_node            
        algorithm = self.__algorithm
        algorithm_class = type(algorithm)
        dialog = Dialog(list(range(repeat_times)), title=algorithm.__name__ + ' Progress')
            
        queue = mp.Queue()
#        all_arg = eval_format('[([], dict({Scripting.convert_args_to_str(**kwargs)}))]*{repeat_times}')
        for k in range(repeat_times):
            mp.Process(target=parallel_func, args=(algorithm_class, k, queue, args, kwargs)).start()        

        @root_node.thread_manager.new_thread_do
        def wait_result():
            t1 = time.clock()

            result_count = 0
            
            while True:
                proc_data = queue.get()
                if proc_data[0] == 'progress':
                    dialog.set_progress(index=proc_data[2], progress=proc_data[1])
                elif proc_data[0] == 'result':
                    result_count += 1
                    root_node.thread_manager.main_thread_do(block=False)(
                        lambda data=proc_data[1]: \
                            self._data_container_command_seq_exec(on_finished, data=data)
                    )
                if result_count == repeat_times:
                    break
                    
            delta_t = time.clock() - t1
            dialog.set_text(index=0, text=auto_subs('Finished. Total time consumption: $delta_t (s)'))

                        
    @property
    def node_path(self):
        if isinstance(self.parent_node, AlgorithmDict):
            return eval_format('{self.parent_node.node_path}["{self.meta.name}"]')
        else:
            return ModelNode.node_path
            
    def presetParams(self, params):
        self.__algorithm.presetParams(params)



def parallel_func(algorithm_class, process_id, queue, args, kwargs):
    algorithm = algorithm_class()
    def default_progressbar(k, K, *args, **kwargs):
        queue.put(('progress', int(k / K * 100), process_id))
    algorithm.progress_checker.append(default_progressbar)
    result = algorithm(*args, **kwargs)
    queue.put(('result', result))



class AlgorithmDict(NodeDict, WindowComponent):
    def __init__(self, node_name=''):
        NodeDict.__init__(self, node_name=node_name)
        
                
    def __setitem__(self, key, val):
        if not isinstance(val, AlgorithmNode):
            raise TypeError(eval_format('{self.node_path} only accepts instance of Algorithm or of its subclasses.'))
        if key != val.meta.name:
            raise ValueError('The key should be identical to the name of the algorithm.')
        NodeDict.__setitem__(self, key, val)
        
        
    def add(self, node):
        self[node['name']] = node
        