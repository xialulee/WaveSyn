# -*- coding: utf-8 -*-
"""
Created on Fri Feb  2 01:19:18 2018

@author: Feng-cong Li
"""
import ast
import inspect



def name_to_glsl(node):
    return node.id



def binop_to_glsl(node):
    opmap = {
        ast.Add: '+',
        ast.Sub: '-',
        ast.Mult: '*',
        ast.Div: '/'}
    left_str = expr_to_glsl(node.left)
    right_str = expr_to_glsl(node.right)
    return f'({left_str}{opmap[type(node.op)]}{right_str})'



def compare_to_glsl(node):
    opmap = {
        ast.Lt: '<',
        ast.LtE: '<=',
        ast.Gt: '>',
        ast.GtE: '>=',
        ast.NotEq: '!='}
    left_str = expr_to_glsl(node.left)
    code_list = [f'({left_str}']
    for op, comparator in zip(node.ops, node.comparators):
        op_str = opmap[type(op)]
        comparator_str = expr_to_glsl(comparator)
        code_list.append(f'{op_str}{comparator_str})')
        code_list.append(f' && ({comparator_str}')
    return ''.join(code_list[:-1])



def expr_to_glsl(node):
    typemap = {
        ast.Name: name_to_glsl,
        ast.BinOp: binop_to_glsl,
        ast.Compare: compare_to_glsl}
    expr_str = typemap[type(node)](node)
    return expr_str



def return_to_glsl(node, indent):
    expr = node.value
    if expr: # return with a value
        expr_str = expr_to_glsl(expr)
    else: # return None
        expr_str = ''
    blanks = ' '*indent
    return f'{blanks}return {expr_str};'



def func_to_glsl(func, delta_indent=4):
    typemap = {
        ast.Return: return_to_glsl}
    code_list = [] # This list of the generated GLSL code strings.
    indent = 0
    
    source = inspect.getsource(func)
    mod_node = ast.parse(source)
    func_node = mod_node.body[0]
    signature = {'args':func_node.args, 'returns':func_node.returns}
    func_name = func_node.name
    
    arg_list = []
    for arg in signature['args'].args:
        arg_list.append(f'{arg.annotation.id} {arg.arg}')
    arg_str = ', '.join(arg_list)
    code_list.append(f'{signature["returns"].id} {func_name}({arg_str}){{')
    indent += delta_indent
    for item in func_node.body:
        code_list.append(typemap[type(item)](item, indent))
    indent -= delta_indent
    code_list.append('}')
    return '\n'.join(code_list)