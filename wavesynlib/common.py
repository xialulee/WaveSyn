# -*- coding: utf-8 -*-
"""
Created on Sat May 17 20:05:23 2014

@author: Feng-cong Li
"""

import sys
from string import Template, Formatter
import threading


class Observable(object):        
    def __init__(self, *args, **kwargs):
        super(Observable, self).__init__(*args, **kwargs)
        self.__observers    = []

    def addObserver(self, observer):
        self.__observers.append(observer)
        
    def deleteObserver(self, observer):
        self.__observers.remove(observer)
        
    def deleteObservers(self):
        self.__observers    = []
        
    def countObservers(self):
        return len(self.__observers)
        
    def notifyObservers(self, *args, **kwargs):
        for observer in self.__observers:
            observer.update(*args, **kwargs)
            
            
class SimpleObserver(object):
    def __init__(self, func):
        self.__func = func

    def update(self, *args, **kwargs):
        return self.__func(*args, **kwargs)              


class MethodDelegator(object):
    def __init__(self, attrName, methodName):
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
    def __init__(self, level=1):
        Formatter.__init__(self)
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
                
#evalFmt = EvalFormatter().format
def evalFmt(formatString):
    return EvalFormatter(level=2).format(formatString)                


class ObjectWithLock(object):    
    '''This is a mixin class.'''
    @property
    def lock(self):
        if not hasattr(self, '_lock'):
            self._lock  = threading.Lock()
        return self._lock
        
        
class Singleton(type):
    '''This class is a meta class, which helps to create singleton class.'''
    def __call__(self, *args, **kwargs):
        if hasattr(self, 'instance'):
            return self.instance
        else:
            self.instance = object.__new__(self)
            # In this circumstance, the __init__ should be called explicitly.
            self.__init__(self.instance, *args, **kwargs)
            return self.instance        