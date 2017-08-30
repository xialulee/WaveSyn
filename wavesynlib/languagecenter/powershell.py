# -*- coding: utf-8 -*-
"""
Created on Tue Dec 29 10:44:36 2015

@author: Feng-cong Li
"""
import ast



class ExprTranslator:
    # This translator is originally posted on "http://blog.sina.com.cn/s/blog_4513dde60101jorh.html"
    opMap = {
        ast.Eq      : '-eq',
        ast.NotEq   : '-ne',
        ast.GtE     : '-ge',
        ast.LtE     : '-le',
        ast.Gt      : '-gt',
        ast.Lt      : '-lt',
        
        ast.Add     : '+',
        ast.Sub     : '-',
        ast.Mult    : '*',
        ast.Div     : '/',
        ast.Mod     : '%',
        
        ast.UAdd    : '+',
        ast.USub    : '-',
        ast.Not     : '-not',
        
        ast.And     : '-and',
        ast.Or      : '-or'
    } 
    
    nameMap     = {
        '_':        '$_'
    }

    
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
            return f'({cls.translate(node.value)}).{node.attr}'
            
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
            ast.Str:        lambda: f'"{node.s}"'
        }[type(node)]()

