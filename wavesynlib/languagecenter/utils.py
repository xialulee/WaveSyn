# -*- coding: utf-8 -*-
"""
Created on Wed Dec 30 19:25:10 2015

@author: Feng-cong Li
"""
from __future__ import print_function, division

import sys
from string import Template, Formatter

def autoSubs(template):
    return Template(template).substitute(sys._getframe(1).f_locals)
    
    
class EvalFormatter(Formatter):
    def __init__(self, level=1):
        super(EvalFormatter, self).__init__()
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
                

def evalFmt(formatString):
    return EvalFormatter(level=2).format(formatString)                