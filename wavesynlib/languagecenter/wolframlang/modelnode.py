# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 00:09:03 2019

@author: Feng-cong Li
"""

from wavesynlib.languagecenter.wavesynscript import Scripting, ModelNode


import os
from pathlib import Path
import hy
try:
    from wavesynlib.languagecenter.wolframlang import jsontranslate
except hy.errors.HyCompilerError:
    hy_path = Path(__file__).parent / 'jsontranslate.hy'
    os.system(f'hyc {hy_path}')
    from wavesynlib.languagecenter.wolframlang import jsontranslate



class Utils(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
    def exprjson_to_func(self, expr_json):
        return jsontranslate.create_func(expr_json)
        