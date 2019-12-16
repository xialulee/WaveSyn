import re


command_str = r"[a-z]\w*"
command_pattern = re.compile(command_str)

sq_str = r"""
'
[^'\\\n]*
(
    \\.
    [^'\\\n]*
)*
'
"""

dq_str = r'''
"
[^"\\\n]*
(
    \\.
    [^"\\\n]*
)*
"
'''

string_str = f"(({sq_str})|({dq_str}))"

string_pattern = re.compile(string_str, re.VERBOSE)

arg_char_class = r"[^'\"\s]"
arg_str = rf"""
(
    {arg_char_class}+
    ({string_str}*{arg_char_class}*)*
) |
(
    {string_str}
    ({arg_char_class}*{string_str}*)*
)
"""

arg_pattern = re.compile(arg_str, re.VERBOSE)