tag = "#wsppl"



def preprocess(linecoll, tag=tag):
    indent_level = 0
    line = linecoll.next()
    if line.lstrip().startswith(tag):
        while True:
            rsline = line.rstrip()
            if rsline[-1]=="\\" and rsline[-2]!="\\":
                try:
                    newline = linecoll.next()
                except StopIteration:
                    raise SyntaxError("Line continuation without new line.")
                line += newline
            else:
                break
    else:
        yield f"{' '*(4*indent_level)}print({repr(line)})"
