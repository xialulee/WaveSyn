# -*- coding: utf-8 -*-
"""
Created on Tue Dec 29 10:44:36 2015

@author: Feng-cong Li
"""
from __future__ import print_function

import json
from copy import deepcopy
import platform
import ast




class ExprTranslator(object):
    # This translator is originally posted on "http://blog.sina.com.cn/s/blog_4513dde60101jorh.html"
    opMap = {
        ast.Eq      : '-eq',
        ast.GtE     : '-ge',
        ast.LtE     : '-le',
        ast.Gt      : '-gt',
        ast.Lt      : '-lt',
        
        ast.Add     : '+',
        ast.Sub     : '-',
        ast.Mult    : '*',
        ast.Div     : '/',
        
        ast.UAdd    : '+',
        ast.USub    : '-',
        ast.Not     : '-not',
        
        ast.And     : '-and',
        ast.Or      : '-or'
    } 
    
    nameMap     = {
        '_':        '$_'
    }
    def __init__(self):
        pass
    
    @classmethod
    def translate(cls, node):
        def comp():
            args = []
            for arg in node.comparators[:-1]:
                argStr  = cls.translate(arg)
                argStr  = '({}) -and ({})'.format(argStr, argStr)
                args.append(argStr)
            args.append(cls.translate(node.comparators[-1]))
            expr    = []
            for op, arg in zip(node.ops, args):
                expr.append(cls.opMap[type(op)])
                expr.append(arg)
            expr.insert(0, cls.translate(node.left))
            return '(' + ' '.join(expr) + ')'
            
        def attr():
            return '({}).{}'.format(cls.translate(node.value), node.attr)
            
        def boolOp():
            return '(({left}) {op} ({right}))'.format(
                op      = cls.opMap[type(node.op)],
                left    = cls.translate(node.values[0]),
                right   = cls.translate(node.values[1])
            )
            

        if isinstance(node, str):
            return cls.translate(ast.parse(node))
        return {
            ast.Module:     lambda: cls.translate(node.body[0]),
            ast.Expr:       lambda: cls.translate(node.value),
            ast.UnaryOp:    lambda: '({op}({operand}))'.format(
                op      = cls.opMap[type(node.op)],
                oprand  = cls.translate(node.operand)
            ),
            ast.BinOp:      lambda: '(({left}) {op} ({right}))'.format(
                op      = cls.opMap[type(node.op)],
                left    = cls.translate(node.left),
                right   = cls.translate(node.right)
            ),
            ast.BoolOp:     boolOp,
            ast.Compare:    comp, 
            ast.Attribute:  attr,
            ast.Name:       lambda: cls.nameMap.get(node.id, node.id),
            ast.Num:        lambda: str(node.n),
            ast.Str:        lambda: '"{}"'.format(node.s)
        }[type(node)]()



class Command(object):
    def __init__(self, commandString):
        self.__comStrList   = [commandString]
        
    def appendArg(self, arg):
        self.__comStrList.append(arg)
        
    @property
    def commandString(self):
        return ' '.join(self.__comStrList)
        
    def where(self, expr, lang='py'):
        newObj  = deepcopy(self)
        if lang == 'py':
            expr    = ExprTranslator.translate(expr)
        newObj.appendArg('| where{' + expr + '}')
        return newObj
            
    def select(self, expr):
        if isinstance(expr, list): # To Do: iteratable objects
            expr = ','.join(expr)
        newObj  = deepcopy(self)
        newObj.appendArg('| ' + 'select ' + expr)
        return newObj

    if platform.system().lower() == 'windows': 
        @property
        def resultObject(self):
            from wavesynlib.interfaces.os.windows import powershell
            tempCom     = self.commandString + ' | ConvertTo-Json'
            stdout, stderr, errorlevel  = powershell.execute(tempCom)
            return json.loads(stdout) # To Do: Handle exceptions
    else:
        @property
        def resultObject(self):
            raise NotImplementedError

        
        
def command(com, *args, **kwargs):
    comObj  = Command(com)
#    if kwargs:
#        for key, value in kwargs:
#            self.__comStrList.append('-'+key)
#            self.__comStrList.append(value)
    for arg in args:
        comObj.appendArg(arg)
    return comObj
    
    
    
if __name__ == '__main__':
    print(command('ps').select('name,id').where('4900 < _.id < 5000').resultObject)
