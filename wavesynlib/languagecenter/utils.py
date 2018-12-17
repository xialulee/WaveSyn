# -*- coding: utf-8 -*-
"""
Created on Wed Dec 30 19:25:10 2015

@author: Feng-cong Li
"""

import sys
import threading
from string import Template, Formatter
from pathlib import Path

import inspect



def auto_subs(template):
    return Template(template).substitute(sys._getframe(1).f_locals)
    
 
    
def get_caller_dir():
    return Path(inspect.getfile(sys._getframe(1))).parent.absolute()



def call_immediately(func):
    func()
    


class EvalFormatter(Formatter):
    def __init__(self, level=1):
        super().__init__()
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
                


def eval_format(format_string):
    return EvalFormatter(level=2).format(format_string) 



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
        lock = getattr(obj, self.__lockName)
        descriptor  = self.__descriptor
        if lock:
            raise AttributeError(f'Method {descriptor.__name__} has been locked and cannot be called.')
        else:
            return self.__descriptor.__get__(obj, type)        
        
        
        
def set_attributes(obj, **kwargs):
    '''This function mimics the VisualBasic "with" statement.'''    
    for attribute_name in kwargs:
        setattr(obj, attribute_name, kwargs[attribute_name])
        


class ObjectWithLock:    
    '''This is a mixin class.'''
    @property
    def lock(self):
        if not hasattr(self, '_lock'):
            self._lock  = threading.Lock()
        return self._lock
        
    

class FunctionChain:
    def __init__(self):
        self.__functions    = []
    
    
    def __call__(self, *args, **kwargs):
        retval = None
        for func in self.__functions:
            retval = func(*args, **kwargs)
        return retval
    
    
    def add_function(self, func):
        self.__functions.append(func)
    
    
    def delete_function(self, func):
        self.__functions.remove(func)
    
    
    def delete_functions(self):
        self.__functions    = []
    
    
    def count_functions(self):
        return len(self.__functions)
    
     

class property_with_args:
    class Property:
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
    
    
        
import ctypes



def ctype_build(type_, doc=''):
    '''\
This decorator is a helper for defining C struct/union datatypes.

An example:
@ctype_build('struct')
def XINPUT_GAMEPAD(
    wButtons: WORD,
    bLeftTrigger: BYTE,
    bRightTrigger: BYTE,
    sThumbLX: SHORT,
    sThumbLY: SHORT,
    sThumbRX: SHORT,
    sThumbRY: SHORT
):pass    
'''
    type_ = type_.lower()
    
    def the_decorator(f):
        field_names = f.__code__.co_varnames[:f.__code__.co_argcount]
        field_types = f.__annotations__
        
        field_desc = []
        anonymous = []
        for name in field_names:
            type_desc = field_types[name]
            if isinstance(type_desc, (list, tuple)):
                for prop in type_desc[1:]:
                    if prop == 'anonymous':
                        anonymous.append(name)
                type_desc = type_desc[0]
            field_desc.append((name, type_desc))
            
        if type_ in ('struct', 'structure'):
            base_class = ctypes.Structure
        elif type_ == 'union':
            base_class = ctypes.Union
        else:
            raise TypeError('Not supported type.')
        
        class TheType(base_class):
            if doc:
                __doc__ = doc
            if anonymous:
                _anonymous_ = anonymous
            _fields_ = field_desc
        return TheType    

    return the_decorator


    
                       