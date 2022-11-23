# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 00:09:03 2019

@author: Feng-cong Li
"""

from wavesynlib.languagecenter.wavesynscript import Scripting, ModelNode



class Utils(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
#    def exprjson_to_func(self, expr_json):
#        expr_json = self.root_node.interfaces.os.clipboard.constant_handler_CLIPBOARD_TEXT(expr_json)
#        return jsontranslate.create_func(expr_json)
        