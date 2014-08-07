# -*- coding: utf-8 -*-
"""
Created on Wed Aug 06 15:57:18 2014

@author: whhit
"""
import thread
import operator
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer

from application    import Application, Scripting
from objectmodel    import ModelNode, NodeList, NodeDict
from common         import evalFmt

# Client

proxy   = None

def initProxy():
    global proxy
    proxy = xmlrpclib.ServerProxy("http://localhost:8000/")


class ProxyNode(object):    
    def __init__(self, nodePath=Scripting.rootName):
        global proxy
        if proxy is None: 
            initProxy()
        self.__nodePath     = nodePath
        self.__reprStr      = proxy.getRepr(nodePath)
        childNodes   = proxy.getChildNodes(nodePath)
        self.childNodes = childNodes
        for nodeName in childNodes:
            self.__dict__[nodeName] = None
            
    def __getattribute__(self, attrName):
        childNodes  = object.__getattribute__(self, 'childNodes')
        if attrName in childNodes:
            return ProxyNode(childNodes[attrName])
        else:
            return object.__getattribute__(self, attrName)
            
    def __repr__(self):
        return self.__reprStr
        
    def __getitem__(self, index):
        return ProxyNode(proxy.getitem(self.__nodePath, index))
            
        

# Server End
#def isNodeList(nodePath=Scripting.rootName):
#    return isinstance(
#        Application.instance.execute(nodePath),
#        NodeList
#    )
#    
#def isNodeDict(nodePath=Scripting.rootName):
#    return isinstance(
#        Application.instance.execute(nodePath),
#        NodeDict
#    )
def getitem(nodePath, index):
    return Application.instance.execute(evalFmt('{nodePath}[{index}].nodePath'))

def getChildNodes(nodePath=Scripting.rootName):
    return Application.instance.execute(evalFmt('{nodePath}.childNodes'))
    
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
        

def startXMLRPCServer(addr='localhost', port=8000):        
    server = SimpleXMLRPCServer((addr, port))
    functions   = [
        #isNodeList,
        #isNodeDict,
        getitem,
        getChildNodes,
        getMethods,
        getRepr
    ]
    for function in functions:
        server.register_function(function, function.__name__)
    thread.start_new_thread(server.serve_forever, tuple())
        