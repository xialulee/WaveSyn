# -*- coding: utf-8 -*-
"""
Created on Mon May 19 22:21:38 2014

@author: Feng-cong Li
"""
    

from common import autoSubs, MethodLock 

# Object Model Sub-System
# It is a part of the scripting system.
   
    
# How to implement a context manager? See:
# http://pypix.com/python/context-managers/        
class AttributeLock(object):
    def __init__(self, node):
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
        

# NodeDict
class NodeDict(ModelNode, dict):
    _xmlrpcexport_  = []    
    
    def __init__(self, nodeName=''):
        dict.__init__(self)
        ModelNode.__init__(self, nodeName=nodeName)
        
    def __setitem__(self, key, val):
        object.__setattr__(val, 'parentNode', self)
        val.lockAttribute('parentNode')
        dict.__setitem__(self, key, val)

# NodeList       
class NodeList(ModelNode, list):
    _xmlrpcexport_  = []
    
    def __init__(self, nodeName=''):
        list.__init__(self)
        ModelNode.__init__(self, nodeName='')
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