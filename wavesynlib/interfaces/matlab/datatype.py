# -*- coding: utf-8 -*-
"""
Created on Fri Jan 01 16:30:34 2016

@author: Feng-cong Li
"""
from abc                 import ABCMeta, abstractproperty, abstractmethod
import datetime

class BaseConverter(object):
    __metaclass__   = ABCMeta 
    
    def server_getter(self):
        raise NotImplementedError
        
    def server_setter(self, val):
        raise NotImplementedError
        
    server  = abstractproperty(server_getter, server_setter)
    
    @abstractproperty
    def matlabTypeName(self):
        raise NotImplementedError
        
    @abstractmethod
    def convert(self, varName):
        raise NotImplementedError
        
    @classmethod
    def __subclasshook__(cls, C):
        if cls is BaseConverter:
            if hasattr(C, 'server') and hasattr(C, 'matlabTypeName') and hasattr(C, 'convert'):
                return True
        return NotImplemented
        
        
class DateTimeConverter(BaseConverter):            
    def __init__(self):
        self.__server   = None
        
    @property
    def server(self):
        return self.__server
        
    @server.setter
    def server(self, val):
        self.__server   = val
    
    @property
    def matlabTypeName(self):
        return 'datetime'
    
    def convert(self, name):
        server      = self.__server
        keys        = ['Year', 'Month', 'Day', 'Hour', 'Minute', 'Second']
        values      = []
        for key in keys:
            values.append(int(server.call('eval', 1, '.'.join([name, key]))[0]))
        return datetime.datetime(*values)        