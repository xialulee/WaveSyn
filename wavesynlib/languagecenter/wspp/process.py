import uuid

tag = "#wspp"

_block_name_prefix = "____wspp_block_"


def generate_block_name():
    uid = uuid.uuid1()
    uid = str(uid)
    uid = uid.replace("-", "_")
    return _block_name_prefix + uid



def preprocess(lineiter, tag=tag):
    indent_level = 0
    stack = []
    while True:
        try:
            line = next(lineiter)
        except StopIteration:
            break
        lsline = line.lstrip()
        if lsline.startswith(tag):
            while True:
                rsline = line.rstrip()
                if rsline[-1]=="\\" and rsline[-2]!="\\":
                    try:
                        newline = next(lineiter)
                    except StopIteration:
                        raise SyntaxError("Line continuation without new line.")
                    line += newline
                else:
                    break
            line = line.replace("\\", " ")
            (delta_indent, indent_now), text, leading = _dispatch(line, stack)
            if indent_now:
                indent_level += delta_indent
            if text is not None:
                yield f"{' '*(4*indent_level)}{text}"
            if not indent_now:
                indent_level += delta_indent
        else:
            yield f"{' '*(4*indent_level)}print({repr(line)})"


def _inst_block(arg, line, stack):
    block_name = generate_block_name()
    stack.append(("block", block_name))
    return (1, False), f"def {block_name}():"


def _inst_endblock(arg, line, stack):
    top = stack.pop(-1)
    if top[0] != "block": 
        raise SyntaxError("Block")
    block_name = top[1]
    return (-1, True), f"{block_name}()"


def _inst_fstr(arg, leading, stack):
    return (0, None), f"print({repr(leading)}+f{repr(arg)})"


def _inst_stmt(arg, leading, stack):
    return (0, None), arg


def _inst_expr(arg, leading, stack):
    return (0, None), f"print({repr(leading)}+str(eval({repr(arg)})))"


def _control_insts(arg, leading, stack, keyword):
    stack.append((keyword,))
    arg = arg.rstrip()
    if arg[-1] != ":":
        arg += ":"
    return (1, False), f"{keyword} {arg}"

def _endcontrol_insts(arg, leading, stack, keyword):
    top = stack.pop(-1)
    if top[0] != keyword:
        raise SyntaxError("")
    return (-1, True), None

def _inst_for(arg, leading, stack):
    return _control_insts(arg, leading, stack, "for")

def _inst_endfor(arg, leading, stack):
    return _endcontrol_insts(arg, leading, stack, "for")

def _inst_if(arg, leading, stack):
    return _control_insts(arg, leading, stack, "if")

def _inst_endif(arg, leading, stack):
    return _endcontrol_insts(arg, leading, stack, "if")
    
def _inst_with(arg, leading, stack):
    return _control_insts(arg, leading, stack, "with")

def _inst_endwith(arg, leading, stack):
    return _endcontrol_insts(arg, leading, stack, "endwith")


_inst_dict = {
    "block":    _inst_block,
    "endblock": _inst_endblock,
    "fstr":     _inst_fstr,
    "stmt":     _inst_stmt,
    "expr":     _inst_expr,
    "if":       _inst_if, 
    "endif":    _inst_endif,
    "for":      _inst_for,
    "endfor":   _inst_endfor,
    "with":     _inst_with,
    "endwith":  _inst_endwith}



def _dispatch(cmd_str, stack):
    cmd = cmd_str.split(maxsplit=2)
    inst = cmd[1]
    try:    
        arg = cmd[2]
    except IndexError:
        arg = None
    leading_cnt = len(cmd_str) - len(cmd_str.lstrip())
    leading = cmd_str[:leading_cnt]
    indent_info, text = _inst_dict[inst](arg, leading, stack)
    return indent_info, text, leading



if __name__ == "__main__":
    test_str = '''
#wspp block 
#wspp stmt \\
pycnt = 100
a = 0;
b = 0;
#wspp if pycnt > 0
#wspp fstr \\
a + b == {pycnt}
#wspp endif
#wspp endblock
'''
    a = 100
    code = []
    for line in preprocess(iter(test_str.split("\n"))):
        print(line)
        #eval(line)
        code.append(line)
    code = "\n".join(code)
    with open("D:/lab/wspp/testpp.py", "w") as f:
        f.write(code)
