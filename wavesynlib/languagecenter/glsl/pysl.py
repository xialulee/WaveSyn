# -*- coding: utf-8 -*-
"""
Created on Fri Feb  2 01:19:18 2018

@author: Feng-cong Li
"""
import ast
import inspect



def name_to_glsl(node):
    return node.id



def num_to_glsl(node):
    return repr(node.n)



def unary_to_glsl(node):
    opmap = {
        ast.Invert: '~',
        ast.Not: '!',
        ast.UAdd: '+',
        ast.USub: '-'}
    expr_str = expr_to_glsl(node.operant)
    return f'{opmap[node.op]}({expr_str})'



def binop_to_glsl(node):
    opmap = {
        ast.Add: '+',
        ast.Sub: '-',
        ast.Mult: '*',
        ast.Div: '/',
        ast.Mod: '%',
        ast.LShift: '<<',
        ast.RShift: '>>',
        ast.BitOr: '|',
        ast.BitXor: '^',
        ast.BitAnd: '&'}
    # Add, Sub, Mult, MatMult, Div, Mod, Pow, LShift, RShift, BitOr, BotXor, BitAnd, FloorDiv
    left_str = expr_to_glsl(node.left)
    right_str = expr_to_glsl(node.right)
    return f'({left_str}{opmap[type(node.op)]}{right_str})'



def boolop_to_glsl(node):
    opmap = {
        ast.And: ' && ',
        ast.Or: ' || '}
    code_list = []
    for item in node.values:
        code_list.append(f'({expr_to_glsl(item)})')
    code = opmap[type(node.op)].join(code_list)
    return f'({code})'



def compare_to_glsl(node):
    opmap = {
        ast.Eq: '==',
        ast.NotEq: '!=',
        ast.Lt: '<',
        ast.LtE: '<=',
        ast.Gt: '>',
        ast.GtE: '>='}
        # ast.Is, ast.IsNot, ast.In, ast.NotIn
    left_str = expr_to_glsl(node.left)
    code_list = [f'({left_str}']
    for op, comparator in zip(node.ops, node.comparators):
        op_str = opmap[type(op)]
        comparator_str = expr_to_glsl(comparator)
        code_list.append(f'{op_str}{comparator_str})')
        code_list.append(f' && ({comparator_str}')
    return ''.join(code_list[:-1])




def ifexp_to_glsl(node):
    test_str = expr_to_glsl(node.test)
    body_str = expr_to_glsl(node.body)
    orelse_str = expr_to_glsl(node.orelse)
    return f'{test_str} ? {body_str} : {orelse_str}'



def expr_to_glsl(node, indent=-1):
    if isinstance(node, ast.Expr):
        node = node.value
    typemap = {
        ast.Name: name_to_glsl,
        ast.Num: num_to_glsl,
        ast.UnaryOp: unary_to_glsl,
        ast.BinOp: binop_to_glsl,
        ast.BoolOp: boolop_to_glsl,
        ast.Compare: compare_to_glsl,
        ast.IfExp: ifexp_to_glsl}
    expr_str = typemap[type(node)](node)
    if indent >= 0:
        expr_str = ' '*indent + expr_str
    return expr_str



def annassign_to_glsl(node, indent):
    expr_str = expr_to_glsl(node.value)
    return f'{" "*indent}{node.annotation.id} {node.target.id} = {expr_str};'



def return_to_glsl(node, indent):
    expr = node.value
    if expr: # return with a value
        expr_str = expr_to_glsl(expr)
    else: # return None
        expr_str = ''
    return f'{" "*indent}return {expr_str};'



def if_to_glsl(node, indent, el=False):
    code_list = []
    test_str = expr_to_glsl(node.test)
    word = '} else if' if el else 'if'
    code_list.append(f'{" "*indent}{word} ({test_str}) {{')
    indent += 4
    for item in node.body:
        code_list.append(stat_to_glsl(item, indent))
    indent -= 4
    if node.orelse:
        if isinstance(node.orelse[0], ast.If):
            code_list.append(if_to_glsl(node.orelse[0], indent, el=True))
        else:
            code_list.append(f'{" "*indent}}} else {{')
            indent += 4
            for item in node.orelse:
                code_list.append(stat_to_glsl(item, indent))
            indent -= 4
     
    if not node.orelse or not isinstance(node.orelse[0], ast.If):
        code_list.append(f'{" "*indent}}}')
    return '\n'.join(code_list)



def stat_to_glsl(node, indent):
    typemap = {
        ast.AnnAssign: annassign_to_glsl,
        ast.If: if_to_glsl,
        ast.Return: return_to_glsl,
        ast.Expr: expr_to_glsl}
    return typemap[type(node)](node, indent)



def func_to_glsl(func, delta_indent=4):
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
        code_list.append(stat_to_glsl(item, indent))
    indent -= delta_indent
    code_list.append('}')
    return '\n'.join(code_list)
