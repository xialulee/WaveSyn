# -*- coding: utf-8 -*-
"""
Created on Sat May 17 20:05:23 2014

@author: Feng-cong Li
"""

import sys
from string import Template

class MethodDelegator(object):
    def __init__(self, attrName, methodName)   :
        self.attrName   = attrName
        self.methodName = methodName
    
    def __get__(self, obj, type=None):
        return getattr(getattr(obj, self.attrName), self.methodName)  
        
        
def setMultiAttr(obj, **kwargs):
    '''This function mimics the VisualBasic "with" statement.'''    
    for attrName in kwargs:
        setattr(obj, attrName, kwargs[attrName])
        
def autoSubs(template):
    return Template(template).substitute(sys._getframe(1).f_locals)