# from .pattern import item_prog
import regex

from .strsubs import SUBS_ENVVAR_STR, SUBS_COMMAND

from wavesynlib.languagecenter.python.pattern import (
    sqstring_noprefix,
    dqstring_noprefix,
    sq3string_noprefix,
    dq3string_noprefix,
    any_)

stringprefix = ""
sqstring = stringprefix + sqstring_noprefix
dqstring = stringprefix + dqstring_noprefix
sq3string = stringprefix + sq3string_noprefix
dq3string = stringprefix + dq3string_noprefix
string_pattern = any_("STRING", [sq3string, dq3string, sqstring, dqstring])

word_pattern = r"""
(?P<WORD>
    (?:
        # If not match escape chars, \ should be excluded.
        [^\s'\"$|&;\\] |
        # Match escape chars.
        (?:\\.)
    )+
)"""

blanks_pattern = r"(?P<BLANKS>\s+)"

op_pattern   = r"""
(?P<OP>
    [|&] |
    $\(  |
    \)
)"""

item_pattern = f"""
    {string_pattern}   |
    {word_pattern}     |
    {op_pattern}       |
    {blanks_pattern}   |
    {SUBS_ENVVAR_STR}  
"""
item_prog = regex.compile(item_pattern, regex.DOTALL | regex.VERBOSE)
brbs_prog = regex.compile(r"\)+$", regex.VERBOSE)



def split(command):
    result = []
    while command:
        match = item_prog.match(command)
        if not match:
            match = SUBS_COMMAND.match(command)
        if not match:
            break
        result.append(match.group(0))
        command = command[match.end():]
    return result


def _remove_leading_blanks(token_list):
    result = [token_list[0]]        
    index = 1
    for index in range(1, len(token_list)):
        if token_list[index].strip():
            break
    result.extend(token_list[index:])
    return result


def group(token_list):
    result = [[""]]
    
    index = 0
    while index < len(token_list):
        token = token_list[index]
        if token == "|":
            result.append(["|"])
            index += 1
            continue
        result[-1].append(token)
        index += 1

    for index, token_list in enumerate(result):
        result[index] = _remove_leading_blanks(token_list)
    return result
