# -*- coding: utf-8 -*-
"""
Created on Sat May 17 20:05:23 2014

@author: Feng-cong Li
"""

import sys
from string import Template, Formatter

class MethodDelegator(object):
    def __init__(self, attrName, methodName)   :
        self.attrName   = attrName
        self.methodName = methodName
    
    def __get__(self, obj, type=None):
        return getattr(getattr(obj, self.attrName), self.methodName)  
        
        
class MethodLock(object):
    def __init__(self, method, lockName):
        self.__descriptor   = method
        self.__lockName     = lockName
        
    def __get__(self, obj, type=None):
        lock    = getattr(obj, self.__lockName)
        descriptor  = self.__descriptor
        if lock:
            raise AttributeError, evalFmt('Method {descriptor.__name__} has been locked and cannot be called.')
        else:
            return self.__descriptor.__get__(obj, type)        
        
        
def setMultiAttr(obj, **kwargs):
    '''This function mimics the VisualBasic "with" statement.'''    
    for attrName in kwargs:
        setattr(obj, attrName, kwargs[attrName])
        
def autoSubs(template):
    return Template(template).substitute(sys._getframe(1).f_locals)
    
    
class EvalFormatter(Formatter):
    def __init__(self):
        Formatter.__init__(self)
        self.caller = [] # Will be set by method "format".
                             
    def get_value(self, expr, args=None, kwargs=None):
        caller   = self.caller        
        return eval(expr, caller[-1].f_globals, caller[-1].f_locals)
        
    def get_field(self, field_name, args, kwargs):
        obj = self.get_value(field_name, args, kwargs)
        return obj, field_name        
        
    def format(self, format_string, *args, **kwargs):
        self.caller.append(sys._getframe(1))
        try:                    
            return Formatter.format(self, format_string, *args, **kwargs)
        finally:            
            self.caller.pop()
                
evalFmt = EvalFormatter().format
