# -*- coding: utf-8 -*-
"""
Created on Fri Jan 01 16:28:10 2016

@author: Feng-cong Li
"""
from datatype import BaseConverter

class Symbol(object):
    def __init__(self, name):
        self.__name     = name
        
    @property
    def name(self):
        return self.__name
        
    def __repr__(self):
        return self.__name
        
        
class Expression(object):
    def __init__(self, tree, variables):
        self.__tree         = tree.replace('\n', '')
        self.__variables    = variables.replace('\n', '')
        
    @property
    def tree(self):
        return self.__tree
        
    @property
    def variables(self):
        return self.__variables 
        
    def __repr__(self):
        return 'vars = {}\ntree = {}'.format(self.__variables, self.__tree)
        
        
class SymConverter(BaseConverter):
    def __init__(self):
        self.__server   = None
    
    @property
    def matlabTypeName(self):
        return 'sym'
        
    @property
    def server(self):
        return self.__server
        
    @server.setter
    def server(self, val):
        self.__server   = val
    
    def convert(self, name):
        server      = self.__server
        tree, var   = server.getMuPadExprTree(name)
        return Expression(tree, var)        