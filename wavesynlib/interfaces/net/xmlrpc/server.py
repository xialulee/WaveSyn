# -*- coding: utf-8 -*-
"""
Created on Wed Aug 06 15:57:18 2014

@author: Feng-cong Li
"""
import six.moves._thread as thread
import operator

from six.moves.xmlrpc_server import SimpleXMLRPCServer

from wavesynlib.application                  import Application
from wavesynlib.languagecenter.utils         import eval_format
from wavesynlib.languagecenter.wavesynscript import Scripting, ScriptCode



# Server End
def getRootNodePath():
    return Scripting.root_name


def getitem(node_path, index):
    return Application.instance.execute(eval_format('{node_path}[{repr(index)}].node_path'))
    # if repr is not used, the index of str type cannot be handled correctly.

def getChildNodes(node_path=Scripting.root_name):
    return Application.instance.execute(eval_format('{node_path}.child_nodes'))
    
def getMethodDoc(node_path, method_name):
    doc = Application.instance.execute(eval_format('{node_path}.{method_name}.__doc__'))    
    return '' if doc is None else doc
    
def getMethods(node_path=Scripting.root_name):
    execute = Application.instance.execute
    nodeObj = execute(node_path)
    mro     = type(nodeObj).__mro__
    return list(set(
        reduce(
            operator.add, [
                classObj._xmlrpcexport_ for classObj in mro if hasattr(classObj, '_xmlrpcexport_')
            ]
        )
    ))    
        
def getRepr(node_path=Scripting.root_name):
    return Application.instance.execute(eval_format('{node_path}.__repr__()'))
  

class CommandSlot(object):
    def __init__(self):
        self.__threadLock   = thread.allocate_lock()
        self.__command      = None
        self.__return_value    = None
        
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
    def return_value(self):
        while True:            
            with self.__threadLock:                
                if self.__return_value is not None:
                    ret = self.__return_value
                    self.__return_value    = None
                    return ret
                    
    @return_value.setter
    def return_value(self, val):
        with self.__threadLock:
            self.__return_value    = val
    

  
def callMethod(node_path, method_name, args, kwargs):
    app = Application.instance
    codeFeature = 'wavesyn_xmlrpcclient_scripting_code'
    args    = [ScriptCode(arg[codeFeature]) if isinstance(arg, dict) and arg.has_key(codeFeature) else arg for arg in args]
    for key in kwargs:
        val = kwargs[key]
        if isinstance(val, dict) and val.has_key(codeFeature):
            kwargs[key] = ScriptCode(val[codeFeature])
    app.xmlrpc_command_slot.command   = (node_path, method_name, args, kwargs)
    ret, err = app.xmlrpc_command_slot.return_value
    if err is not None:
        raise err
    return 0 if ret is None else ret
    
        

def start_xmlrpc_server(addr='localhost', port=8000):        
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
        