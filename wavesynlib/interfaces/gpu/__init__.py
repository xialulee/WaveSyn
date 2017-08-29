# -*- coding: utf-8 -*-
"""
Created on Sat Apr 22 17:11:01 2017

@author: Feng-cong Li
"""
from wavesynlib.languagecenter.wavesynscript import ModelNode



class GPU(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cuda_worker = ModelNode(
            is_lazy=True,
            module_name='wavesynlib.interfaces.gpu.cuda',
            class_name='Worker'
        )
