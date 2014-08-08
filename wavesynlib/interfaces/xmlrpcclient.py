# -*- coding: utf-8 -*-
"""
Created on Fri Aug 08 15:11:33 2014

@author: Feng-cong Li
"""
import xmlrpclib

class code:
    def __init__(self, code):
        self.wavesyn_xmlrpcclient_scripting_code   = code
    
    
class Proxy(object):
    def __init__(self, addr='http://localhost', port=8000):
        self.__proxy    = xmlrpclib.ServerProxy(':'.join((addr, str(port))))
        
    @property
    def proxy(self):
        return self.__proxy
        
    def getRootNode(self):
        nodePath    = self.__proxy.getRootNodePath()
        return ProxyNode(self.__proxy, nodePath)


class ProxyNode(object):    
    def __init__(self, proxy, nodePath):
        self.nodePath   = nodePath
        self.__proxy    = proxy
        self.__reprStr  = proxy.getRepr(nodePath)
        childNodes  = proxy.getChildNodes(nodePath)
        methods     = set(proxy.getMethods(nodePath))
        self.childNodes = childNodes
        self.methods    = methods
        for nodeName in childNodes:
            self.__dict__[nodeName] = None
        for method in methods:
            self.__dict__[method]   = None
            
    def __getattribute__(self, attrName):
        childNodes  = object.__getattribute__(self, 'childNodes')
        methods     = object.__getattribute__(self, 'methods')
        nodePath    = object.__getattribute__(self, 'nodePath')
        if attrName in childNodes:
            return ProxyNode(self.__proxy, childNodes[attrName])
        elif attrName in methods:
            method  = ProxyMethod(self.__proxy, nodePath, attrName)
            return method
        else:
            return object.__getattribute__(self, attrName)
            
    def __repr__(self):
        return self.__reprStr
        
    def __getitem__(self, index):
        return ProxyNode(self.__proxy, self.__proxy.getitem(self.nodePath, index))
            
class ProxyMethod(object):
    def __init__(self, proxy, nodePath, methodName):
        self.__nodePath = nodePath
        self.__proxy    = proxy
        self.__methodName   = methodName
        self.__doc__        = proxy.getMethodDoc(nodePath, methodName)        
        
    def __call__(self, *args, **kwargs):
        return self.__proxy.callMethod(self.__nodePath, self.__methodName, args, kwargs)