# -*- coding: utf-8 -*-
"""
Created on Wed Aug 06 15:57:18 2014

@author: whhit
"""
import thread
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer

from application    import Application, Scripting
from common         import evalFmt

# Client

proxy   = None

def initProxy():
    global proxy
    proxy = xmlrpclib.ServerProxy("http://localhost:8000/")


class ProxyNode(object):    
    def __init__(self, nodePath=Scripting.rootName):
        global proxy
        if proxy is None: initProxy()
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
            
        

# Server End

def getChildNodes(nodePath=Scripting.rootName):
    return Application.instance.execute(evalFmt('{nodePath}.childNodes'))
        
def getRepr(nodePath=Scripting.rootName):
    return Application.instance.execute(evalFmt('{nodePath}.__repr__()'))
        

def startXMLRPCServer(addr='localhost', port=8000):        
    server = SimpleXMLRPCServer((addr, port))
    server.register_function(getChildNodes, "getChildNodes")
    server.register_function(getRepr,       'getRepr')
    thread.start_new_thread(server.serve_forever, tuple())
        