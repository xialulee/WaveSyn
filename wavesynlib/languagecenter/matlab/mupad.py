# -*- coding: utf-8 -*-
"""
Created on Wed Dec 30 22:47:05 2015

@author: Feng-cong Li

Originally posted on my blog:
http://blog.sina.com.cn/s/blog_4513dde60101pkho.html
"""
from __future__ import print_function

from scipy                           import special


from wavesynlib.languagecenter.utils     import auto_subs, eval_format
from wavesynlib.toolboxes.matlab.mupad  import Symbol

class OperatorMap(object):
    def __init__(self):
        self.__opMap    = {
            '_plus':    '+',
            '_mult':    '*',
            '_power':   '**'
        }
    
    def __getitem__(self, key):
        return self.__opMap[key]
        
    def __contains__(self, key):
        return key in self.__opMap
        
operatorMap     = OperatorMap()

class FunctionMap(object):
    def __init__(self):
        self.__funcMap  = {
            'igamma':   self.igammaTranslate
        }
        
    def __getitem__(self, key):
        return self.__funcMap[key]
        
    def __contains__(self, key):
        return key in self.__funcMap
        
    def igammaTranslate(self, a, x):
        return auto_subs('(special.gamma($a) * special.gammaincc($a, $x))')
        
functionMap     = FunctionMap()


        
        
def exprTreeStrToSymList(treeStr):
    class LocalNameSpace(object):
        def __getitem__(self, key):
            return Symbol(key)
            
    tree    = eval(treeStr, {}, LocalNameSpace())
    return tree
    
    
def varListStrToSymList(varListStr):
    class LocalNameSpace(object):
        def __init__(self):
            self.syms   = []
            
        def __getitem__(self, key):
            return Symbol(key)
            
    localSpace  = LocalNameSpace()
    return eval(varListStr, {}, localSpace)
    
    
def symListToScipy(symList, varList):
    def _symListToSciPy(symList): # To Do: Function arguments translation (some homonymic functions of MuPad and SciPy have different arguments definitions)
        try:
            iter(symList)
        except TypeError:
            symList     = [symList]
        head, tail      = symList[0], symList[1:]
        if not tail:
            return repr(head)
            
        newTail     = [_symListToSciPy(item) for item in tail]
        if head.name in operatorMap: # head is an operator
            op  = operatorMap[head.name]
            return eval_format('({op.join(newTail)})')
        elif head.name in functionMap: # head is function needs arguments translation
            return functionMap[head.name](*newTail)
        else: # head is a function without argument translation
            return eval_format('{head.name}({",".join(newTail)})')
        
            
    exprStr     = _symListToSciPy(symList)
    varStr      = ','.join([sym.name for sym in varList])
    codeStr     = eval_format('lambda {varStr}: {exprStr}')
    return eval(codeStr), codeStr