# -*- coding: utf-8 -*-
"""
Created on Sat Mar 04 21:02:17 2017

@author: Feng-cong Li
"""
import json
import abc
from comtypes import client



class SWbemSink(metaclass=abc.ABCMeta):
    def __init__(self, *args, **kwrags):
        pass
    
    
    def ISWbemSinkEvents_OnObjectReady(self, this, objWbemObject, objWbemAsyncContext):
        self.on_object_ready(objWbemObject, objWbemAsyncContext)
    
    
    @abc.abstractmethod    
    def on_object_ready(self, wbem_object, context):
        pass
    
    
    def ISWbemSinkEvents_OnCompleted(self, this,
        iHResult, objWbemErrorObject, objWbemAsyncContext):
        self.on_completed(iHResult, objWbemErrorObject, objWbemAsyncContext)
        
        
    @abc.abstractmethod
    def on_completed(self, hresult, error_object, context):
        pass
    
    
    def ISWbemSinkEvents_OnProgress(self, this,
        iUpperBound, iCurrent, strMessage, objWbemAsyncContext):
        self.on_progress(iUpperBound, iCurrent, strMessage, objWbemAsyncContext)
        
        
    @abc.abstractmethod
    def on_progress(self, upper_bound, current, message, context):
        pass
    
    
    def ISWbemSinkEvents_OnObjectPut(self, this, objWbemObjectPath, objWbemAsyncContext):
        self.on_object_put(objWbemObjectPath, objWbemAsyncContext)
        
        
    @abc.abstractmethod
    def on_object_put(self, object_path, context):
        pass



class WQL:
    def __init__(self, services):
        self.__services = services
        self.__connection = None
        self.__com_sink = None
        
        
    def query(self, wql_str, output_format='original'):
        items = self.__services.ExecQuery(wql_str)

        def to_native(items):
            result = []
            for item in items:
                d = {}
                for prop in item.Properties_:
                    d[prop.Name] = prop.Value
                result.append(d)
            return result
            
        def to_json(items):
            result = to_native(items)
            return json.dumps(result)
        
        def identity(items):
            return items
        
        return {
            'original': identity,
            'comtypes': identity,
            'native': to_native,
            'python': to_native,
            'json': to_json
        }[output_format](items)
        
        
    def set_sink(self, sink, wql_str):
        self.__com_sink = com_sink = client.CreateObject('WbemScripting.SWbemSink')
        py_sink = sink
        self.__connection = client.GetEvents(com_sink, py_sink)
        self.__services.ExecNotificationQueryAsync(com_sink, wql_str)
        