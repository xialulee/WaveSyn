tag = "#wspp"



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
            delta_indent, text, leading = _dispatch(line, stack)
            indent_level += delta_indent
            yield f"{' '*(4*indent_level)}{text}"
        else:
            yield f"{' '*(4*indent_level)}print({repr(line)})"



def _inst_fstr(arg, leading, stack):
    return 0, f"print({repr(leading)}+f{repr(arg)})"

def _inst_expr(arg, leading, stack):
    return 0, f"print({repr(leading)}+str(eval({repr(arg)})))"

_inst_dict = {
    "fstr": _inst_fstr,
    "expr": _inst_expr }



def _dispatch(cmd_str, stack):
    cmd = cmd_str.split(maxsplit=2)
    inst = cmd[1]
    arg = cmd[2]
    leading_cnt = len(cmd_str) - len(cmd_str.lstrip())
    leading = cmd_str[:leading_cnt]
    delta_indent, text = _inst_dict[inst](arg, leading, stack)
    return delta_indent, text, leading



if __name__ == "__main__":
    test_str = '''
a = 0;
b = 0;
    #wspp fstr\\
    pass {a}
    #wspp expr\\
    1+2
    #wspp fstr\\
    {", ".join(str(i) for i in range(10))}
    '''
    a = 100
    for line in preprocess(iter(test_str.split("\n"))):
        #print(line)
        eval(line)
