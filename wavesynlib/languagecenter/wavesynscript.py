# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 16:15:12 2015

@author: Feng-cong Li
"""
from __future__ import print_function, division, unicode_literals

import sys

from wavesynlib.languagecenter.utils import auto_subs, eval_format, MethodLock


# Object Model of the Scripting System
# It is a part of the scripting system.
       
# How to implement a context manager? See:
# http://pypix.com/python/context-managers/        
class AttributeLock(object):
    def __init__(self, node):
        super(AttributeLock, self).__init__()
        if not isinstance(node, ModelNode):
            raise TypeError, 'Only the instance of ModelNode is accepted.'
        self.node   = node
            
    def __enter__(self):
        self.node.attribute_auto_lock = True
        return self.node
        
    def __exit__(self, *dumb):
        self.node.attribute_auto_lock = False
        
        
# To Do: Implement an on_bind callback which is called when a node is connecting to the tree.    
class ModelNode(object):
    _xmlrpcexport_  = []    
    
    def __init__(self, node_name='', is_root=False, **kwargs):
        super(ModelNode, self).__init__()
        if '_attribute_lock' not in self.__dict__:
            object.__setattr__(self, '_attribute_lock', set())
        self.parentNode = None
        self.__is_root = is_root
        self.node_name = node_name
        #self.attribute_auto_lock   = False
        
    def lock_attribute(self, attribute_name, lock=True):
        '''Lock a specified attribute, i.e. the attribute cannot be re-assigned.
For example:        
node.a = 0
node.lock_attribute("a")
If you try to give node.a a new value
node.a = 1
then an AttributeError will be raised.
'''
        if lock:
            self._attribute_lock.add(attribute_name)
        else:
            if attribute_name in self._attribute_lock:
                self._attribute_lock.remove(attribute_name)
        
    @property
    def attribute_lock(self):
        '''This attribute is in fact a context manager.
if the following statements are executed:
with node.attribute_lock:
  node.a = 0
then node will have a property named 'a', which cannot be re-assigned.
'''
        return AttributeLock(self)        
        
    @property
    def is_root(self):
        return self.__is_root
        
    def __setattr__(self, key, val):
        if '_attribute_lock' not in self.__dict__:
            # This circumstance happens when __setattr__ called before __init__ being called.
            object.__setattr__(self, '_attribute_lock', set())
        if 'attribute_auto_lock' not in self.__dict__:
            object.__setattr__(self, 'attribute_auto_lock', False)
        if key in self._attribute_lock:
            raise AttributeError, auto_subs('Attribute "$key" is unchangeable.')
        if isinstance(val, ModelNode) and not val.is_root and val.parentNode==None:
            val.node_name = val.node_name if val.node_name else key
            object.__setattr__(val, 'parentNode', self)
            
            # The autolock mechanism will lock the node after you attach it to the model tree.
            # A child node cannot change its parent
            val.lock_attribute('parentNode')
            # and the parent node's child node cannot be re-assinged. 
            self.lock_attribute(key)
                    
        object.__setattr__(self, key, val)
        if self.attribute_auto_lock and key != 'attribute_auto_lock': # attribute_auto_lock cannot be locked
            self.lock_attribute(key)        
        
    @property
    def node_path(self):
        if self.is_root:
            return self.node_name
        else:
            return '.'.join((self.parentNode.node_path, self.node_name))
            
    @property
    def child_nodes(self):
        return {attribute_name:self.__dict__[attribute_name].node_path for attribute_name in self.__dict__ 
            if isinstance(self.__dict__[attribute_name], ModelNode)} 
            
    @property
    def root_node(self):
        node    = self
        while not node.is_root:
            node    = node.parentNode
        return node
        

class Dict(dict, object):
    def __init__(self, *args, **kwargs):
        super(Dict, self).__init__()

# NodeDict
class NodeDict(ModelNode, Dict):
    _xmlrpcexport_  = []    
    
    def __init__(self, node_name=''):
        super(NodeDict, self).__init__(node_name=node_name)
        
    def __setitem__(self, key, val):
        object.__setattr__(val, 'parentNode', self)
        val.lock_attribute('parentNode')
        dict.__setitem__(self, key, val)


class List(list, object):
    def __init__(self, *args, **kwargs):
        super(List, self).__init__()

# NodeList       
class NodeList(ModelNode, List):
    _xmlrpcexport_  = []
    
    def __init__(self, node_name=''):
        super(NodeList, self).__init__(node_name=node_name)
        self.__element_lock = True

    
    def lock_elements(self, lock=True):
        self.__element_lock = lock
        
    def append(self, val):
        object.__setattr__(val, 'parentNode', self)        
        list.append(self, val)
        val.index   = len(self) - 1
        val.lock_attribute('index')


    @property
    def element_lock(self):
        return self.__element_lock
        
    def __update_index(method):
        def func(self, *args, **kwargs):            
            try:
                ret = method(self, *args, **kwargs)
            finally:
                for index, val in enumerate(self):
                    val.lock_attribute('index', lock=False)
                    val.index   = index
                    val.lock_attribute('index', lock=True)
            return ret
        func.__name__   = method.__name__
        func.__doc__    = method.__doc__
        return func

    for method_name in ('__delitem__', '__delslice__', '__setitem__', 'pop', 'remove', 'reverse', 'sort', 'insert'):
        locals()[method_name]    = MethodLock(method=__update_index(getattr(list, method_name)), lockName='element_lock')    
# End Object Model


# Scripting Sub-System
class ScriptCode(object):
    def __init__(self, code):
        self.code = code
        
class Scripting(ModelNode):
    _xmlrpcexport_  = []    
    
    root_name = 'wavesyn' # The name of the object model tree's root
    root_node = None
    name_space = {'locals':{}, 'globals':{}}
    
    _print_code_flag = False
    
    @staticmethod
    def convert_args_to_str(*args, **kwargs):
        def paramToStr(param):
            if isinstance(param, ScriptCode):
                return param.code
            else:
                return repr(param)
                
        strArgs = ', '.join([paramToStr(arg) for arg in args]) if args else ''
        strKwargs = ', '.join([eval_format('{key}={paramToStr(kwargs[key])}') for key in kwargs]) \
            if kwargs else ''        
       
            
        if strArgs and strKwargs:
            params = ', '.join((strArgs, strKwargs))
        else:
            params = strArgs if strArgs else strKwargs
        return params
        
    def __init__(self, root_node):
        super(Scripting, self).__init__()
        self.__root_node = root_node
            
    def executeFile(self, filename):
        execfile(filename, **self.name_space) #?
                
    @classmethod    
    def printable(cls, method):
        def func(self, *args, **kwargs):
            if cls._print_code_flag:
                try:
                    cls._print_code_flag = False # Prevent recursive.
                    ret = cls.root_node.print_and_eval(
                        eval_format(
                            '{self.node_path}.{method.__name__}({Scripting.convert_args_to_str(*args, **kwargs)})'
                        )
                    )
                finally:
                    cls._print_code_flag = True # Restore _print_code_flag settings.
            else:                          
                ret = method(self, *args, **kwargs)
            return ret
        func.__doc__    = method.__doc__
        func.__name__   = method.__name__
        return func  


class CodePrinter(object):            
    def __enter__(self):
        Scripting._print_code_flag = True
        
    def __exit__(self, *dumb):
        Scripting._print_code_flag = False
        

code_printer = CodePrinter()                                 
# End Scripting Sub-System
        

