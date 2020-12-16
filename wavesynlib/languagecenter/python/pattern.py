# -*- coding: utf-8 -*-
"""
Created on Fri Jun 16 15:00:08 2017

@author: Feng-cong Li
"""

import keyword
import builtins
import re






def any_(name, alternates):
    "Return a named group pattern matching list of alternates."
    # Copied from idlelib.colorizer
    return "(?P<%s>" % name + "|".join(alternates) + ")"



kw = r"\b" + any_("KEYWORD", keyword.kwlist) + r"\b"
builtinlist = [str(name) for name in dir(builtins)
                                    if not name.startswith('_') and \
                                    name not in keyword.kwlist]
# self.file = open("file") :
# 1st 'file' colorized normal, 2nd as builtin, 3rd as string
builtin = r"([^.'\"\\#]\b|^)" + any_("BUILTIN", builtinlist) + r"\b"
comment = any_("COMMENT", [r"#[^\n]*"])
stringprefix = r"(?i:\br|u|f|fr|rf|b|br|rb)?"
sqstring = stringprefix + r"'[^'\\\n]*(\\.[^'\\\n]*)*'?"
dqstring = stringprefix + r'"[^"\\\n]*(\\.[^"\\\n]*)*"?'
sq3string = stringprefix + r"'''[^'\\]*((\\.|'(?!''))[^'\\]*)*(''')?"
dq3string = stringprefix + r'"""[^"\\]*((\\.|"(?!""))[^"\\]*)*(""")?'
string = any_("STRING", [sq3string, dq3string, sqstring, dqstring])



def make_pat():
    # Copied from idlelib.colorizer
    return kw + "|" + builtin + "|" + comment + "|" + string +\
           "|" + any_("SYNC", [r"\n"])
           
           

prog = re.compile(make_pat(), re.S)
