# -*- coding: utf-8 -*-
"""
Created on Fri Feb  2 01:19:18 2018

@author: Feng-cong Li
"""
import ast
import inspect



def type_max(*args):
    type_idx = {int:0, float:1}
    current = 0
    type_ = int
    for arg in args:
        if current < type_idx[arg]:
            current = type_idx[arg]
            type_ = arg
    return type_



def name_to_glsl(node):
    return node.id, None



def num_to_glsl(node):
    n = node.n
    return repr(n), type(n)



def unary_to_glsl(node):
    opmap = {
        ast.Invert: '~',
        ast.Not: '!',
        ast.UAdd: '+',
        ast.USub: '-'}
    expr_str, type_ = expr_to_glsl(node.operant)
    return f'{opmap[node.op]}({expr_str})', type_



def call_to_glsl(node):
    func_name = node.func.id
    arg_list = []
    for arg in node.args:
        arg_list.append(expr_to_glsl(arg)[0])
    return f'{func_name}({", ".join(arg_list)})', None



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
    left_str, type_left = expr_to_glsl(node.left)
    right_str, type_right = expr_to_glsl(node.right)
    return f'({left_str}{opmap[type(node.op)]}{right_str})', type_max(type_left, type_right)



def boolop_to_glsl(node):
    opmap = {
        ast.And: ' && ',
        ast.Or: ' || '}
    code_list = []
    for item in node.values:
        code_list.append(f'({expr_to_glsl(item)[0]})')
    code = opmap[type(node.op)].join(code_list)
    return f'({code})', int



def compare_to_glsl(node):
    opmap = {
        ast.Eq: '==',
        ast.NotEq: '!=',
        ast.Lt: '<',
        ast.LtE: '<=',
        ast.Gt: '>',
        ast.GtE: '>='}
        # ast.Is, ast.IsNot, ast.In, ast.NotIn
    left_str, type_ = expr_to_glsl(node.left)
    code_list = [f'({left_str}']
    for op, comparator in zip(node.ops, node.comparators):
        op_str = opmap[type(op)]
        comparator_str, type_ = expr_to_glsl(comparator)
        code_list.append(f'{op_str}{comparator_str})')
        code_list.append(f' && ({comparator_str}')
    return ''.join(code_list[:-1]), int




def ifexp_to_glsl(node):
    test_str = expr_to_glsl(node.test)
    body_str, type_ = expr_to_glsl(node.body)
    orelse_str, type_ = expr_to_glsl(node.orelse)
    return f'{test_str} ? {body_str} : {orelse_str}', type_



def expr_to_glsl(node, indent=-1):
    if isinstance(node, ast.Expr):
        node = node.value
    typemap = {
        ast.Name: name_to_glsl,
        ast.Num: num_to_glsl,
        ast.UnaryOp: unary_to_glsl,
        ast.Call: call_to_glsl,
        ast.BinOp: binop_to_glsl,
        ast.BoolOp: boolop_to_glsl,
        ast.Compare: compare_to_glsl,
        ast.IfExp: ifexp_to_glsl}
    expr_str, type_ = typemap[type(node)](node)
    if indent >= 0:
        expr_str = ' '*indent + expr_str
    return expr_str, type_



def annassign_to_glsl(node, indent):
    expr_str, type_ = expr_to_glsl(node.value)
    return f'{" "*indent}{node.annotation.id} {node.target.id} = {expr_str};'



def assign_to_glsl(node, indent):
    expr_str, type_ = expr_to_glsl(node.value)
    if not type_:
        raise TypeError('Type inference failed.')
    type_map = {int:'int', float:'float'}
    return f'{" "*indent}{type_map[type_]} {node.targets[0].id} = {expr_str};'



def return_to_glsl(node, indent):
    expr = node.value
    if expr: # return with a value
        expr_str, type_ = expr_to_glsl(expr)
    else: # return None
        expr_str = ''
    return f'{" "*indent}return {expr_str};'



def if_to_glsl(node, indent, el=False):
    code_list = []
    test_str, type_ = expr_to_glsl(node.test)
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
        ast.Assign: assign_to_glsl,
        ast.If: if_to_glsl,
        ast.Return: return_to_glsl,
        ast.Expr: lambda node, indent: expr_to_glsl(node, indent)[0]}
    return typemap[type(node)](node, indent)



def func_to_glsl(func, delta_indent=4):
    code_list = [] # This list of the generated GLSL code strings.
    indent = 0
    
    if isinstance(func, str):
        source = func
    else:
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




def module_to_glsl(source):
    code_list = []
    module = ast.parse(source)
    for body in module.body:
        code_list.append(stat_to_glsl(body, indent=0))
    return '\n'.join(code_list)



if __name__ == '__main__':
    source = '''    
def hit_circle(xy:vec2, center:vec2, radius:float, tol:float)->float:
    d:float = distance(center, xy)
    lower:float = radius - tol
    upper:float = radius + tol
    if lower < d < upper:
        return (tol-abs(d-radius)) / tol
    else:
        return 0.0
'''

    print(func_to_glsl(source))
