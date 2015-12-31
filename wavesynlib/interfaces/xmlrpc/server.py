# -*- coding: utf-8 -*-
"""
Created on Wed Aug 06 15:57:18 2014

@author: Feng-cong Li
"""
import thread
import operator

from SimpleXMLRPCServer import SimpleXMLRPCServer

from wavesynlib.application                  import Application
from wavesynlib.languagecenter.utils         import evalFmt
from wavesynlib.languagecenter.wavesynscript import Scripting, ScriptCode



# Server End
def getRootNodePath():
    return Scripting.rootName


def getitem(nodePath, index):
    return Application.instance.execute(evalFmt('{nodePath}[{repr(index)}].nodePath'))
    # if repr is not used, the index of str type cannot be handled correctly.

def getChildNodes(nodePath=Scripting.rootName):
    return Application.instance.execute(evalFmt('{nodePath}.childNodes'))
    
def getMethodDoc(nodePath, methodName):
    doc = Application.instance.execute(evalFmt('{nodePath}.{methodName}.__doc__'))    
    return '' if doc is None else doc
    
def getMethods(nodePath=Scripting.rootName):
    execute = Application.instance.execute
    nodeObj = execute(nodePath)
    mro     = type(nodeObj).__mro__
    return list(set(
        reduce(
            operator.add, [
                classObj._xmlrpcexport_ for classObj in mro if hasattr(classObj, '_xmlrpcexport_')
            ]
        )
    ))    
        
def getRepr(nodePath=Scripting.rootName):
    return Application.instance.execute(evalFmt('{nodePath}.__repr__()'))
  

class CommandSlot(object):
    def __init__(self):
        self.__threadLock   = thread.allocate_lock()
        self.__command      = None
        self.__returnVal    = None
        
    @property
    def command(self):
        with self.__threadLock:
            cmd = self.__command
            self.__command  = None
            return cmd
            
    @command.setter
    def command(self, command):
        while True:
            if self.command is None:
                with self.__threadLock:
                    self.__command  = command
            break
        
    @property
    def returnVal(self):
        while True:            
            with self.__threadLock:                
                if self.__returnVal is not None:
                    ret = self.__returnVal
                    self.__returnVal    = None
                    return ret
                    
    @returnVal.setter
    def returnVal(self, val):
        with self.__threadLock:
            self.__returnVal    = val
    

  
def callMethod(nodePath, methodName, args, kwargs):
    app = Application.instance
    codeFeature = 'wavesyn_xmlrpcclient_scripting_code'
    args    = [ScriptCode(arg[codeFeature]) if isinstance(arg, dict) and arg.has_key(codeFeature) else arg for arg in args]
    for key in kwargs:
        val = kwargs[key]
        if isinstance(val, dict) and val.has_key(codeFeature):
            kwargs[key] = ScriptCode(val[codeFeature])
    app.xmlrpcCommandSlot.command   = (nodePath, methodName, args, kwargs)
    ret, err = app.xmlrpcCommandSlot.returnVal
    if err is not None:
        raise err
    return 0 if ret is None else ret
    
        

def startXMLRPCServer(addr='localhost', port=8000):        
    server = SimpleXMLRPCServer((addr, port))
    functions   = [
        getRootNodePath,
        getitem,
        getChildNodes,
        getMethods,
        getMethodDoc,
        getRepr,
        callMethod
    ]
    for function in functions:
        server.register_function(function, function.__name__)
    thread.start_new_thread(server.serve_forever, tuple())
    return server
        