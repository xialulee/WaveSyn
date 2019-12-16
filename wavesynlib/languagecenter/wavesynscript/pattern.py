import re



sq3string = r"""
# '''abc\(def\)ghi'''
# abc   [match (1)]
# \(def [match (2)]
# \)ghi [match (2)]
'''
[^'\\]*         # (1)
(
    (
        \\.     # Escape
        |       # or
        '(?!'') # sq not part of str-stop
    )
    [^'\\]*     
)*              # (2)
(?P<closed>''')?  # With or without a str-stop.
"""

sq3pattern = re.compile(sq3string, re.VERBOSE | re.DOTALL)


dq3string = r'''
"""
[^"\\]*
(
    (
        \\.
        |
        "(?!"")
    )
    [^"\\]*
)*
(?P<closed>""")?
'''

dq3pattern = re.compile(dq3string, re.VERBOSE | re.DOTALL)


def detect_q3str(code):
    match_sq3 = re.search(sq3pattern, code)
    match_dq3 = re.search(dq3pattern, code)
    if match_sq3:
        return match_sq3, sq3pattern, "'"
    elif match_dq3:
        return match_dq3, dq3pattern, '"'
    else:
        return None, None, None
