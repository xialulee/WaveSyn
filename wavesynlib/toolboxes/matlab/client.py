# -*- coding: utf-8 -*-
"""
Created on Sat Dec 26 15:06:30 2015

@author: Feng-cong Li
"""

from comtypes            import byref, client, COMError
from comtypes.safearray  import safearray_as_ndarray
from comtypes.automation import VARIANT

from numpy import array, ndarray, isrealobj

from wavesynlib.languagecenter.utils import auto_subs, eval_format

from os.path import abspath, dirname

import inspect



def get_my_dir():
    return abspath(dirname(inspect.getfile(inspect.currentframe())))
    

from datatype             import BaseConverter, DateTimeConverter
from mupad                import SymConverter         
    
    

class MatlabCOMServer(object): # To Do: an instance attribute. For some functions, if they found instance is not None, then they will not create a new instance of this class.
    class NameSpace(object):
        def __init__(self, matlabObj, namespace): 
            self.__matlab_object    = matlabObj
            self.__namespace    = namespace
            
        def __get_available_name(self):
            for k in range(1048576): # Try to find an available name not used in the workspace. Or execute global name before continuing.
                try:
                    name        = 'wavesyn_temp_variable' + str(k) 
                    self[name]  
                except COMError: # find a name not in the namespace
                    retval      = name
                    break   
            return retval
            
            
        def __getitem__(self, name): # To Do: Remove global workspace support
            if self.__matlab_object.call('eval', 1, auto_subs('isnumeric($name)'))[0]:
                if self.__matlab_object.call('eval', 1, auto_subs('isreal($name)'))[0]:
                    with safearray_as_ndarray:
                        retval  = self.__matlab_object.handle.GetVariable(name, self.__namespace)
                else:
                    tempReal    = self.__get_available_name() 
                    try:
                        self.__matlab_object.execute(auto_subs('$tempReal = real($name);'))
                        with safearray_as_ndarray:
                            realPart    = self.__matlab_object.handle.GetVariable(tempReal, self.__namespace)
                    finally:
                        self.__matlab_object.execute(auto_subs('clear $tempReal'))
                    
                    tempImag    = self.__get_available_name()  
                    try:
                        self.__matlab_object.execute(auto_subs('$tempImag = imag($name);'))
                        with safearray_as_ndarray:
                            imagPart    = self.__matlab_object.handle.GetVariable(tempImag, self.__namespace)                    
                    finally:
                        self.__matlab_object.execute(auto_subs('clear $tempImag'))

                    retval  = realPart + 1j * imagPart
            else:
                mtype   = str(self.__matlab_object.call('eval', 1, auto_subs('class($name)'))[0]) # The result is unicode. Convert to str.
                converter   = self.__matlab_object.get_type_converter(mtype)
                if not converter:
                    raise TypeError(auto_subs('Matlab type "$mtype" is not supported.'))
                retval      = converter(name)
            return retval
            
        def __setitem__(self, name, value):
            if not isinstance(value, ndarray):
                value   = array(value)
            if not isrealobj(value):                
                self.__matlab_object.handle.PutFullMatrix(name, self.__namespace, value.real, value.imag)                
            else:
                self.__matlab_object.handle.PutWorkspaceData(name, self.__namespace, value)
    
    matlab_program_id  = 'matlab.application'
    
    def __init__(self):
        self.__handle               = client.CreateObject(self.matlab_program_id)
        self.__base                 = self.NameSpace(self, 'base')
        self.__global               = self.NameSpace(self, 'global')
        self.__type_converter        = {}
        self.add_type_converter(DateTimeConverter())
        self.add_type_converter(SymConverter())
        self.execute(f'addpath {get_my_dir()}')
        
        
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
        
    def get_mupad_exprtree(self, symName):
        return self.call('eval', 2, auto_subs('wavesyn_matlab.get_mupad_exprtree($symName)'))
        
    def add_type_converter(self, converter):
        if not isinstance(converter, BaseConverter):
            raise TypeError('The given converter does not support BaseConverter protocol.')
        converter.server    = self
        self.__type_converter[converter.matlabTypeName]  = converter.convert
        
    def get_type_converter(self, typeName):
        try:
            return self.__type_converter[typeName]
        except KeyError:
            return None
        
    @property
    def handle(self):
        return self.__handle   
        
    @property
    def process_id(self):
        return self.call('wavesyn_matlab.get_process_id', 1)[0]
        
    @property
    def base_namespace(self):
        return self.__base
        
    @property # Remove global workspace read support
    def global_namespace(self):
        return self.__global