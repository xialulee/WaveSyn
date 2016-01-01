# -*- coding: utf-8 -*-
"""
Created on Sat Dec 26 15:06:30 2015

@author: Feng-cong Li
"""

from comtypes            import byref, client, COMError
from comtypes.safearray  import safearray_as_ndarray
from comtypes.automation import VARIANT

from numpy import array, ndarray, isrealobj

from wavesynlib.languagecenter.utils import autoSubs, evalFmt

from os.path import abspath, dirname

import inspect
def selfDir():
    return abspath(dirname(inspect.getfile(inspect.currentframe())))
    

from datatype             import BaseConverter, DateTimeConverter
from mupad                import SymConverter         
    
    

class MatlabCOMServer(object): # To Do: an instance attribute. For some functions, if they found instance is not None, then they will not create a new instance of this class.
    class NameSpace(object):
        def __init__(self, matlabObj, nameSpace): 
            self.__matlabObj    = matlabObj
            self.__nameSpace    = nameSpace
            
        def __getAvailableName(self):
            for k in range(1048576): # Try to find an available name not used in the workspace. Or execute global name before continuing.
                try:
                    name        = 'wavesyn_temp_variable' + str(k) 
                    self[name]  
                except COMError: # find a name not in the namespace
                    retval      = name
                    break   
            return retval
            
            
        def __getitem__(self, name): # To Do: Remove global workspace support
            if self.__matlabObj.call('eval', 1, autoSubs('isnumeric($name)'))[0]:
                if self.__matlabObj.call('eval', 1, autoSubs('isreal($name)'))[0]:
                    with safearray_as_ndarray:
                        retval  = self.__matlabObj.handle.GetVariable(name, self.__nameSpace)
                else:
                    tempReal    = self.__getAvailableName() 
                    try:
                        self.__matlabObj.execute(autoSubs('$tempReal = real($name);'))
                        with safearray_as_ndarray:
                            realPart    = self.__matlabObj.handle.GetVariable(tempReal, self.__nameSpace)
                    finally:
                        self.__matlabObj.execute(autoSubs('clear $tempReal'))
                    
                    tempImag    = self.__getAvailableName()  
                    try:
                        self.__matlabObj.execute(autoSubs('$tempImag = imag($name);'))
                        with safearray_as_ndarray:
                            imagPart    = self.__matlabObj.handle.GetVariable(tempImag, self.__nameSpace)                    
                    finally:
                        self.__matlabObj.execute(autoSubs('clear $tempImag'))

                    retval  = realPart + 1j * imagPart
            else:
                mtype   = str(self.__matlabObj.call('eval', 1, autoSubs('class($name)'))[0]) # The result is unicode. Convert to str.
                converter   = self.__matlabObj.getTypeConverter(mtype)
                if not converter:
                    raise TypeError(autoSubs('Matlab type "$mtype" is not supported.'))
                retval      = converter(name)
            return retval
            
        def __setitem__(self, name, value):
            if not isinstance(value, ndarray):
                value   = array(value)
            if not isrealobj(value):                
                self.__matlabObj.handle.PutFullMatrix(name, self.__nameSpace, value.real, value.imag)                
            else:
                self.__matlabObj.handle.PutWorkspaceData(name, self.__nameSpace, value)
    
    progID  = 'matlab.application'
    
    def __init__(self):
        self.__handle               = client.CreateObject(self.progID)
        self.__base                 = self.NameSpace(self, 'base')
        self.__global               = self.NameSpace(self, 'global')
        self.__typeConverter        = {}
        self.addTypeConverter(DateTimeConverter())
        self.addTypeConverter(SymConverter())
        self.execute(evalFmt('addpath {selfDir()}'))
        
        
    def release(self):
        return self.__handle.Release()
        
    def close(self):
        return self.__handle.Quit()
        
    def call(self, fname, nOut, *args): # To Do: Properly handle complex return values 
        retval  = VARIANT()
        self.__handle.Feval(fname, nOut, byref(retval), *args)
        return retval.value
        
    def execute(self, command):
        with safearray_as_ndarray:
            retval  = self.__handle.Execute(command)
        return retval
        
    def getMuPadExprTree(self, symName):
        return self.call('eval', 2, autoSubs('wavesyn_matlab.getMuPadExprTree($symName)'))
        
    def addTypeConverter(self, converter):
        if not isinstance(converter, BaseConverter):
            raise TypeError('The given converter does not support BaseConverter protocol.')
        converter.server    = self
        self.__typeConverter[converter.matlabTypeName]  = converter.convert
        
    def getTypeConverter(self, typeName):
        try:
            return self.__typeConverter[typeName]
        except KeyError:
            return None
        
    @property
    def handle(self):
        return self.__handle   
        
    @property
    def processId(self):
        return self.call('wavesyn_matlab.getProcessId', 1)[0]
        
    @property
    def nsBase(self):
        return self.__base
        
    @property # Remove global workspace read support
    def nsGlobal(self):
        return self.__global