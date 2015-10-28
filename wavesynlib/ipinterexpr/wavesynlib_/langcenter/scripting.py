# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 21:07:59 2015

@author: Feng-cong Li
"""
import sys
from ..objectmodel import ModelNode
from ..common      import evalFmt

from ..application import Application

# Scripting Sub-System
class ScriptCode(object):
    def __init__(self, code):
        self.code = code
        
class Scripting(ModelNode):
    _xmlrpcexport_  = []    
    
    rootName = 'wavesyn' # The name of the object model tree's root
    nameSpace = {'locals':{}, 'globals':{}}
    
    @staticmethod
    def paramsToStr(*args, **kwargs):
        def paramToStr(param):
            if isinstance(param, ScriptCode):
                return param.code
            else:
                return repr(param)
                
        strArgs = ', '.join([paramToStr(arg) for arg in args]) if args else ''
        strKwargs = ', '.join([evalFmt('{key}={paramToStr(kwargs[key])}') for key in kwargs]) \
            if kwargs else ''        
       
            
        if strArgs and strKwargs:
            params = ', '.join((strArgs, strKwargs))
        else:
            params = strArgs if strArgs else strKwargs
        return params
        
    def __init__(self, rootNode):
        super(Scripting, self).__init__()
        self.__rootNode = rootNode
            
    def executeFile(self, filename):
        execfile(filename, **self.nameSpace) #?
                
    @staticmethod    
    def printable(method):
        def func(self, *args, **kwargs):
            callerLocals    = sys._getframe(1).f_locals
            #####################################
            #print(method.__name__, True if 'printCode' in callerLocals else False)
            #####################################            
            if 'printCode' in callerLocals and callerLocals['printCode']:
                ret = Application.instance.printAndEval(
                    evalFmt(
                        '{self.nodePath}.{method.__name__}({Scripting.paramsToStr(*args, **kwargs)})'
                    )
                )
            else:                          
                ret = method(self, *args, **kwargs)
            return ret
        func.__doc__    = method.__doc__
        func.__name__   = method.__name__
        return func

                                   
# End Scripting Sub-System