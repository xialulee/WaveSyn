# -*- coding: utf-8 -*-
"""
Created on Wed Dec 30 19:25:10 2015

@author: Feng-cong Li
"""
from __future__ import print_function, division

import os
import sys
import threading
from string import Template, Formatter

import inspect

def auto_subs(template):
    return Template(template).substitute(sys._getframe(1).f_locals)
    
    
def get_caller_dir():
    return os.path.abspath(os.path.dirname(inspect.getfile(sys._getframe(1))))    
    
class EvalFormatter(Formatter):
    def __init__(self, level=1):
        super(EvalFormatter, self).__init__()
        self.caller = None # Will be set by method "format".
        self.level  = level
                             
    def get_value(self, expr, args=None, kwargs=None):
        caller   = self.caller        
        return eval(expr, caller.f_globals, caller.f_locals)
        
    def get_field(self, field_name, args, kwargs):
        obj = self.get_value(field_name, args, kwargs)
        return obj, field_name        
        
    def format(self, format_string, *args, **kwargs):
        self.caller = sys._getframe(self.level)
        return Formatter.format(self, format_string, *args, **kwargs)
                

def eval_format(formatString):
    return EvalFormatter(level=2).format(formatString) 


class MethodDelegator(object):
    def __init__(self, attribute_name, method_name):
        super(MethodDelegator, self).__init__()
        self.attribute_name   = attribute_name
        self.method_name = method_name
    
    def __get__(self, obj, type=None):
        return getattr(getattr(obj, self.attribute_name), self.method_name)  
        
        
class MethodLock(object):
    def __init__(self, method, lockName):
        super(MethodLock, self).__init__()
        self.__descriptor   = method
        self.__lockName     = lockName
        
    def __get__(self, obj, type=None):
        lock    = getattr(obj, self.__lockName)
        descriptor  = self.__descriptor
        if lock:
            raise AttributeError, eval_format('Method {descriptor.__name__} has been locked and cannot be called.')
        else:
            return self.__descriptor.__get__(obj, type)        
        
        
def set_attributes(obj, **kwargs):
    '''This function mimics the VisualBasic "with" statement.'''    
    for attribute_name in kwargs:
        setattr(obj, attribute_name, kwargs[attribute_name])
        

class ObjectWithLock(object):    
    '''This is a mixin class.'''
    @property
    def lock(self):
        if not hasattr(self, '_lock'):
            self._lock  = threading.Lock()
        return self._lock
        

class FunctionChain(object):
    def __init__(self):
        super(FunctionChain, self).__init__()
        self.__functions    = []
    
    def __call__(self, *args, **kwargs):
        retval     = None
        for func in self.__functions:
            retval     = func(*args, **kwargs)
        return retval
    
    def addFunction(self, func):
        self.__functions.append(func)
    
    def deleteFunction(self, func):
        self.__functions.remove(func)
    
    def deleteFunctions(self):
        self.__functions    = []
    
    def countFunction(self):
        return len(self.__functions)
    
     
class Nonblocking(object):
    class TheThread(threading.Thread):
        def __init__(self, func, args, kwargs):
            self.func   = func
            self.args   = args
            self.kwargs = kwargs
            self.retval = None
            threading.Thread.__init__(self)
        def run(self):
            ret = self.func(*self.args, **self.kwargs)
            self.retval = ret            
            
    def __init__(self, func):
        super(Nonblocking, self).__init__()
        self.__doc__    = func.__doc__
        self.__func     = func
        self.__thread   = None
        
    def __call__(self, *args, **kwargs):
        self.__thread   = self.TheThread(self.__func, args, kwargs)
        self.__thread.start()
        return self
        
    def isRunning(self):
        if self.__thread is None:
            return False
        return self.__thread.is_alive()
        
    @property
    def return_value(self):
        if self.isRunning():
            return None
        else:
            return self.__thread.retval
      
        
class property_with_args(object):
    class Property(object):
        def __init__(self, instance, func):
            self.__instance = instance
            self.__func = func
        
        def __getitem__(self, args):
            return self.__func(self.__instance, args)
    
    def __init__(self, func):
        self.__func = func
        self.__doc__ = func.__doc__
        
        
    def __get__(self, instance, owner):
        return self.Property(instance, self.__func)
        
                       