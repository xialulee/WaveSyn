# -*- coding: utf-8 -*-
"""
Created on Wed May 29 13:37:26 2019

@author: Feng-cong Li
"""

import os
import hy
from pathlib import Path

try:
    from wavesynlib.languagecenter.unicode.hyutils import text_decoration
except hy.errors.HyCompileError:
    node_path = Path(__file__).parent / 'hyutils.hy'
    os.system(f'hyc {node_path}')
    from wavesynlib.languagecenter.unicode.hyutils import text_decoration
    
    
    
from wavesynlib.languagecenter.wavesynscript import ModelNode



class UnicodeUtils(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
    def text_decoration(self, text, arg):
        return text_decoration(text, arg)
        