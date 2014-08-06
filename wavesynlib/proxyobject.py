# -*- coding: utf-8 -*-
"""
Created on Wed Aug 06 15:57:18 2014

@author: whhit
"""

class ProxyNode(object):
    def __init__(self, nodePath=None):
        self.__nodePath   = nodePath
    
    @property
    def nodePath(self):
        return self.__nodePath
        
        
    def __call__(self, *args, **kwargs):
        self
        
    def invoke(self):
        pass