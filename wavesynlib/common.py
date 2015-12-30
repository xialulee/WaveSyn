# -*- coding: utf-8 -*-
"""
Created on Sat May 17 20:05:23 2014

@author: Feng-cong Li
"""

import threading
from wavesynlib.languagecenter.utils import evalFmt


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
        super(SimpleObserver, self).__init__()
        self.__func = func

    def update(self, *args, **kwargs):
        return self.__func(*args, **kwargs)              


class MethodDelegator(object):
    def __init__(self, attrName, methodName):
        super(MethodDelegator, self).__init__()
        self.attrName   = attrName
        self.methodName = methodName
    
    def __get__(self, obj, type=None):
        return getattr(getattr(obj, self.attrName), self.methodName)  
        
        
class MethodLock(object):
    def __init__(self, method, lockName):
        super(MethodLock, self).__init__()
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
        return self.__thread.isAlive()
        
    @property
    def returnValue(self):
        if self.isRunning():
            return None
        else:
            return self.__thread.retval
                
        
        
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