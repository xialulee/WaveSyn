# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 16:15:12 2015

@author: Feng-cong Li
"""
from __future__                      import print_function, division

import sys

from wavesynlib.languagecenter.utils import autoSubs, evalFmt, MethodLock



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
        self.node.autoLockAttribute = True
        return self.node
        
    def __exit__(self, *dumb):
        self.node.autoLockAttribute = False
        
        
    
class ModelNode(object):
    _xmlrpcexport_  = []    
    
    def __init__(self, nodeName='', isRoot=False, **kwargs):
        super(ModelNode, self).__init__()
        if '_attributeLock' not in self.__dict__:
            object.__setattr__(self, '_attributeLock', set())
        self.parentNode = None
        self.__isRoot = isRoot
        self.nodeName = nodeName
        #self.autoLockAttribute   = False
        
    def lockAttribute(self, attrName, lock=True):
        '''Lock a specified attribute, i.e. the attribute cannot be re-assigned.
For example:        
node.a = 0
node.lockAttribute("a")
If you try to give node.a a new value
node.a = 1
then an AttributeError will be raised.
'''
        if lock:
            self._attributeLock.add(attrName)
        else:
            if attrName in self._attributeLock:
                self._attributeLock.remove(attrName)
        
    @property
    def attributeLock(self):
        '''This attribute is in fact a context manager.
if the following statements are executed:
with node.attributeLock:
  node.a = 0
then node will have a property named 'a', which cannot be re-assigned.
'''
        return AttributeLock(self)        
        
    @property
    def isRoot(self):
        return self.__isRoot
        
    def __setattr__(self, key, val):
        if '_attributeLock' not in self.__dict__:
            # This circumstance happens when __setattr__ called before __init__ being called.
            object.__setattr__(self, '_attributeLock', set())
        if 'autoLockAttribute' not in self.__dict__:
            object.__setattr__(self, 'autoLockAttribute', False)
        if key in self._attributeLock:
            raise AttributeError, autoSubs('Attribute "$key" is unchangeable.')
        if isinstance(val, ModelNode) and not val.isRoot and val.parentNode==None:
            val.nodeName = val.nodeName if val.nodeName else key
            object.__setattr__(val, 'parentNode', self)
            
            # The autolock mechanism will lock the node after you attach it to the model tree.
            # A child node cannot change its parent
            val.lockAttribute('parentNode')
            # and the parent node's child node cannot be re-assinged. 
            self.lockAttribute(key)
                    
        object.__setattr__(self, key, val)
        if self.autoLockAttribute and key != 'autoLockAttribute': # autoLockAttribute cannot be locked
            self.lockAttribute(key)        
        
    @property
    def nodePath(self):
        if self.isRoot:
            return self.nodeName
        else:
            return '.'.join((self.parentNode.nodePath, self.nodeName))
            
    @property
    def childNodes(self):
        return {attrName:self.__dict__[attrName].nodePath for attrName in self.__dict__ 
            if isinstance(self.__dict__[attrName], ModelNode)}            
        

class Dict(dict, object):
    def __init__(self, *args, **kwargs):
        super(Dict, self).__init__()

# NodeDict
class NodeDict(ModelNode, Dict):
    _xmlrpcexport_  = []    
    
    def __init__(self, nodeName=''):
        super(NodeDict, self).__init__(nodeName=nodeName)
        
    def __setitem__(self, key, val):
        object.__setattr__(val, 'parentNode', self)
        val.lockAttribute('parentNode')
        dict.__setitem__(self, key, val)


class List(list, object):
    def __init__(self, *args, **kwargs):
        super(List, self).__init__()

# NodeList       
class NodeList(ModelNode, List):
    _xmlrpcexport_  = []
    
    def __init__(self, nodeName=''):
        super(NodeList, self).__init__(nodeName=nodeName)
        self.__elemLock = True

    
    def lockElements(self, lock=True):
        self.__elemLock = lock
        
    def append(self, val):
        object.__setattr__(val, 'parentNode', self)        
        list.append(self, val)
        val.index   = len(self) - 1
        val.lockAttribute('index')


    @property
    def elemLock(self):
        return self.__elemLock
        
    def __refreshIndex(method):
        def func(self, *args, **kwargs):            
            try:
                ret = method(self, *args, **kwargs)
            finally:
                for idx, val in enumerate(self):
                    val.lockAttribute('index', lock=False)
                    val.index   = idx
                    val.lockAttribute('index', lock=True)
            return ret
        func.__name__   = method.__name__
        func.__doc__    = method.__doc__
        return func

    for methodName in ('__delitem__', '__delslice__', '__setitem__', 'pop', 'remove', 'reverse', 'sort', 'insert'):
        locals()[methodName]    = MethodLock(method=__refreshIndex(getattr(list, methodName)), lockName='elemLock')    
# End Object Model





# Scripting Sub-System
class ScriptCode(object):
    def __init__(self, code):
        self.code = code
        
class Scripting(ModelNode):
    _xmlrpcexport_  = []    
    
    rootName    = 'wavesyn' # The name of the object model tree's root
    rootNode    = None
    nameSpace   = {'locals':{}, 'globals':{}}
    
    @staticmethod
    def paramsToStr(*args, **kwargs):
        def paramToStr(param):
            if isinstance(param, ScriptCode):
                return param.code
            else:
                return repr(param)
                
        strArgs = ', '.join([paramToStr(arg) for arg in args]) if args else ''
        strKwargs = ', '.join([evalFmt('{key}={paramToStr(kwargs[key])}') for key in kwargs]) \
            if kwargs else ''        
       
            
        if strArgs and strKwargs:
            params = ', '.join((strArgs, strKwargs))
        else:
            params = strArgs if strArgs else strKwargs
        return params
        
    def __init__(self, rootNode):
        super(Scripting, self).__init__()
        self.__rootNode = rootNode
            
    def executeFile(self, filename):
        execfile(filename, **self.nameSpace) #?
                
    @classmethod    
    def printable(cls, method):
        def func(self, *args, **kwargs):
            callerLocals    = sys._getframe(1).f_locals
            #####################################
            #print(method.__name__, True if 'printCode' in callerLocals else False)
            #####################################            
            if 'printCode' in callerLocals and callerLocals['printCode']:
                ret = cls.rootNode.printAndEval(
                    evalFmt(
                        '{self.nodePath}.{method.__name__}({Scripting.paramsToStr(*args, **kwargs)})'
                    )
                )
            else:                          
                ret = method(self, *args, **kwargs)
            return ret
        func.__doc__    = method.__doc__
        func.__name__   = method.__name__
        return func                                   
# End Scripting Sub-System
        

