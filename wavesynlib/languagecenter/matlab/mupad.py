# -*- coding: utf-8 -*-
"""
Created on Wed Dec 30 22:47:05 2015

@author: Feng-cong Li

Originally posted on my blog:
http://blog.sina.com.cn/s/blog_4513dde60101pkho.html
"""
from wavesynlib.languagecenter.utils import evalFmt

class OperatorMap(object):
    def __init__(self):
        self.__opMap    = {
            '_plus':    '+',
            '_mult':    '*',
            '_power':   '**'
        }
    
    def __getitem__(self, key):
        return self.__opMap[key]
        
operatorMap     = OperatorMap()

class Symbol(object):
    def __init__(self, name):
        self.__name     = name
        
    @property
    def name(self):
        return self.__name
        
    def __repr__(self):
        return self.__name
        
        
def exprTreeStrToSymList(treeStr):
    class LocalNameSpace(object):
        def __getitem__(self, key):
            return Symbol(key)
            
    tree    = eval(treeStr, {}, LocalNameSpace())
    return tree
    
    
def symListToSciPy(symList): # To Do: Function arguments translation (some homonymic functions of MuPad and SciPy have different arguments definitions)
    try:
        iter(symList)
    except TypeError:
        symList     = [symList]
    head, tail      = symList[0], symList[1:]
    if not tail:
        return repr(head)
    try:
        newTail     = [symListToSciPy(item) for item in tail]
        op          = operatorMap[head.name]
        return evalFmt('({op.join(newTail)})')
    except KeyError: # Function call
        return evalFmt('{head.name}({",".join(newTail)})')