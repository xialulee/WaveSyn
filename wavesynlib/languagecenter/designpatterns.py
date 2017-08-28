# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 18:29:15 2015

@author: Feng-cong Li
"""
class SimpleObserver:
    def __init__(self, func):
        super().__init__()
        self.__func = func
        

    def update(self, *args, **kwargs):
        return self.__func(*args, **kwargs) 



class Observable:        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Notice. Though Observable does not have an explicit parent class, 
        # we should still call the super().__init__(), since it play the role 
        # of a mixin base class which means it has been used for multi-inheritance,
        # and if super init is not called, the initialization chain will be broken. 
        self.__observers = []


    def add_observer(self, observer):
        if not hasattr(observer, 'update'):
            if callable(observer):
                observer = SimpleObserver(observer)
            else:
                raise TypeError('Give observer is not valid.')
        self.__observers.append(observer)        

        
    def delete_observer(self, observer):
        self.__observers.remove(observer)

        
    def delete_all_observers(self):
        self.__observers    = []

        
    def count_observers(self):
        return len(self.__observers)

        
    def notify_observers(self, *args, **kwargs):
        for observer in self.__observers:
            observer.update(*args, **kwargs)
            

            
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