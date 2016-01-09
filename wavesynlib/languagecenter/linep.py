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
    string_prefix   = r"(\br|u|ur|R|U|UR|Ur|uR|b|B|br|Br|bR|BR)?"
    string_pattern  = '|'.join([
        string_prefix + r"'''[^'\\]*((\\.|'(?!''))[^'\\]*)*(''')?",
        string_prefix + r'"""[^"\\]*((\\.|"(?!""))[^"\\]*)*(""")?',
        string_prefix + r"'[^'\\\n]*(\\.[^'\\\n]*)*'?",
        string_prefix + r'"[^"\\\n]*(\\.[^"\\\n]*)*"?'
    ])
    string_pattern = '(?P<STRING>%s)' % string_pattern
    regex = '|'.join([commentPattern, string_pattern])
    return re.compile(regex, re.S)
    
#reCodeSplit = make_split_regex()    
#    
#def codeSplitter(code):
#    pass