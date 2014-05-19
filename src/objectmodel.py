# -*- coding: utf-8 -*-
"""
Created on Mon May 19 22:21:38 2014

@author: Feng-cong Li
"""
    

from common import autoSubs 

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
    def __init__(self, nodeName='', isRoot=False, **kwargs):
        if '_attributeLock' not in self.__dict__:
            object.__setattr__(self, '_attributeLock', set())
        self.parentNode = None
        self.__isRoot = isRoot
        self.nodeName = nodeName
        #self.autoLockAttribute   = False
        
    def lockAttribute(self, attrName):
        '''Lock a specified attribute, i.e. the attribute cannot be re-assigned.
For example:        
node.a = 0
node.lockAttribute("a")
If you try to give node.a a new value
node.a = 1
then an AttributeError will be raised.
'''
        self._attributeLock.add(attrName)
        
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
        

# NodeDict
# NodeList                        
# End Object Model