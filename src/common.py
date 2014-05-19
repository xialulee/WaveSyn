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
        
        
def setMultiAttr(obj, **kwargs):
    '''This function mimics the VisualBasic "with" statement.'''    
    for attrName in kwargs:
        setattr(obj, attrName, kwargs[attrName])
        
def autoSubs(template):
    return Template(template).substitute(sys._getframe(1).f_locals)
    
    
class AdvancedFormatter(Formatter):
    def __init__(self, *args, **kwargs):
        Formatter.__init__(self, *args, **kwargs)
        self.caller = None # Will be set by method "format".
                
#    def check_unused_args(self, used_args, args, kwargs):
#        return        
        
    def get_value(self, expr, args=None, kwargs=None):
        caller   = self.caller        
        return eval(expr, caller.f_globals, caller.f_locals)
        
    def get_field(self, field_name, args, kwargs):
        obj = self.get_value(field_name, args, kwargs)
        return obj, field_name        
        
    def format(self, format_string, *args, **kwargs):
        self.caller = sys._getframe(1)
        return Formatter.format(self, format_string, *args, **kwargs)