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
        node_path    = self.__proxy.getRootNodePath()
        return ProxyNode(self.__proxy, node_path)


class ProxyNode(object):    
    def __init__(self, proxy, node_path):
        self.node_path   = node_path
        self.__proxy    = proxy
        self.__reprStr  = proxy.getRepr(node_path)
        child_nodes  = proxy.getChildNodes(node_path)
        methods     = set(proxy.getMethods(node_path))
        self.child_nodes = child_nodes
        self.methods    = methods
        for node_name in child_nodes:
            self.__dict__[node_name] = None
        for method in methods:
            self.__dict__[method]   = None
            
    def __getattribute__(self, attribute_name):
        child_nodes  = object.__getattribute__(self, 'child_nodes')
        methods     = object.__getattribute__(self, 'methods')
        node_path    = object.__getattribute__(self, 'node_path')
        if attribute_name in child_nodes:
            return ProxyNode(self.__proxy, child_nodes[attribute_name])
        elif attribute_name in methods:
            method  = ProxyMethod(self.__proxy, node_path, attribute_name)
            return method
        else:
            return object.__getattribute__(self, attribute_name)
            
    def __repr__(self):
        return self.__reprStr
        
    def __getitem__(self, index):
        return ProxyNode(self.__proxy, self.__proxy.getitem(self.node_path, index))
            
class ProxyMethod(object):
    def __init__(self, proxy, node_path, method_name):
        self.__node_path = node_path
        self.__proxy    = proxy
        self.__method_name   = method_name
        self.__doc__        = proxy.getMethodDoc(node_path, method_name)        
        
    def __call__(self, *args, **kwargs):
        return self.__proxy.callMethod(self.__node_path, self.__method_name, args, kwargs)