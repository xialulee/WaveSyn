# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 20:52:38 2015

@author: Feng-cong Li
"""

import re
from string import Template

class VPTemplate(Template): # Template for handling variable pool
    idpattern  = '[_a-z0-9]*'
    
def make_split_regex():
    commentPattern = r'(?P<COMMENT>#[^\n]*)'
    stringPrefix   = r"(\br|u|ur|R|U|UR|Ur|uR|b|B|br|Br|bR|BR)?"
    stringPattern  = '|'.join([
        stringPrefix + r"'''[^'\\]*((\\.|'(?!''))[^'\\]*)*(''')?",
        stringPrefix + r'"""[^"\\]*((\\.|"(?!""))[^"\\]*)*(""")?',
        stringPrefix + r"'[^'\\\n]*(\\.[^'\\\n]*)*'?",
        stringPrefix + r'"[^"\\\n]*(\\.[^"\\\n]*)*"?'
    ])
    stringPattern = '(?P<STRING>%s)' % stringPattern
    regex = '|'.join([commentPattern, stringPattern])
    return re.compile(regex, re.S)
    
reCodeSplit = make_split_regex()    
    
def codeSplitter(code):
    pass