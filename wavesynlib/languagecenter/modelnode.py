# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 16:59:26 2015

@author: Feng-cong Li
"""
from wavesynlib.languagecenter.wavesynscript import ModelNode
from wavesynlib.languagecenter.wavesynscript.modelnode import WaveSynScriptNode

    
class LangCenterNode(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wavesynscript = WaveSynScriptNode()

        self.python = ModelNode(
            is_lazy=True,
            module_name='wavesynlib.languagecenter.python.modelnode',
            class_name='Python')
        
        self.html_utils = ModelNode(
            is_lazy=True,
            module_name='wavesynlib.languagecenter.html.modelnode',
            class_name='Utils')
        
        self.markdown_utils = ModelNode(
            is_lazy=True,
            module_name='wavesynlib.languagecenter.markdown.modelnode',
            class_name='Utils')
        
