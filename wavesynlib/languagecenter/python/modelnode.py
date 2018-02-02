# -*- coding: utf-8 -*-
"""
Created on Sat Feb  3 00:45:22 2018

@author: Feng-cong Li
"""

from wavesynlib.languagecenter.wavesynscript import ModelNode



class Python(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table_utils = ModelNode(
            is_lazy=True,
            module_name='wavesynlib.languagecenter.python.utils',
            class_name='TableUtils')
        
