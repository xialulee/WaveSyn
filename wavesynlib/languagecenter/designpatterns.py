# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 18:29:15 2015

@author: Feng-cong Li
"""

class Observable(object):        
    def __init__(self, *args, **kwargs):
        super(Observable, self).__init__(*args, **kwargs)
        self.__observers    = []

    def add_observer(self, observer):
        self.__observers.append(observer)
        
    def deleteObserver(self, observer):
        self.__observers.remove(observer)
        
    def deleteObservers(self):
        self.__observers    = []
        
    def countObservers(self):
        return len(self.__observers)
        
    def notify_observers(self, *args, **kwargs):
        for observer in self.__observers:
            observer.update(*args, **kwargs)
            
            
class SimpleObserver(object):
    def __init__(self, func):
        super(SimpleObserver, self).__init__()
        self.__func = func

    def update(self, *args, **kwargs):
        return self.__func(*args, **kwargs)   



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