# -*- coding: utf-8 -*-
"""
Created on Sat Apr 22 17:11:01 2017

@author: Feng-cong Li
"""
import _thread as thread
from queue import Queue
from reikna import cluda
from wavesynlib.languagecenter.wavesynscript import ModelNode



class Worker(ModelNode):
    def __init__(self, *args, **kwargs):
        api_type = kwargs.pop('api_type').lower()
        if api_type == 'cuda':
            api = cluda.cuda_api
        elif api_type in ('opencl', 'cl', 'ocl'):
            api = cluda.ocl_api
        
        super().__init__(*args, **kwargs)
        try:
            self.__api = api()
        except:
            self.__available = False
            raise NotImplementedError
        self.__message_in = Queue()
        self.__message_out = Queue()
        self.__thr = None
        self.__active = False        
        self.__busy = False
        self.__available = True
        
        
    @property
    def available(self):
        return self.__available
        
        
    @property
    def message_in(self):
        return self.__message_in
        
        
    @property
    def message_out(self):
        return self.__message_out
        
        
    @property
    def reikna_thread(self):
        return self.__thr
    
    
    @property
    def reikna_api(self):
        return self.__api
        
        
    @property
    def is_active(self):
        return self.__active
        
        
    @property 
    def is_busy(self):
        return self.__busy
        
    
    def activate(self):
        if not self.__active:
            thread.start_new_thread(self.__thread_func, ())
            self.__active   = True
            
            
    def create_proc(self, factory, *args, **kwargs):
        return factory.create(self.__thr, *args, **kwargs)
    
    
    def __thread_func(self):
        self.__thr = self.__api.Thread.create()
        while True:
            msg     = self.message_in.get()
            self.__busy = True
            try:
                command = msg['command']
                if command == 'exit':
                    break
                elif command == 'call':
                    func    = msg['callable object']
                    args    = msg['args']
                    kwargs  = msg['kwargs']
                    ret = func(*args, **kwargs)
                    self.message_out.put({'report':'function return', 'return value':ret})
            finally:
                self.__busy = False
        self.__thr.release()
        self.__active   = False



class GPU(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cuda_worker = ModelNode(
            is_lazy=True,
            class_object=Worker,
            init_kwargs={'api_type':'cuda'}
        )
        self.opencl_worker = ModelNode(
            is_lazy=True,
            class_object=Worker,
            init_kwargs={'api_type':'cl'}
        )
