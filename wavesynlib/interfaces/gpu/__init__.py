# -*- coding: utf-8 -*-
"""
Created on Sat Apr 22 17:11:01 2017

@author: Feng-cong Li
"""
from __future__ import print_function, division, unicode_literals

from wavesynlib.languagecenter.wavesynscript import ModelNode



class GPU(ModelNode):
    def __init__(self, *args, **kwargs):
        super(GPU, self).__init__(*args, **kwargs)
        self.cuda_worker = ModelNode(
            is_lazy=True,
            module_name='wavesynlib.interfaces.gpu.cuda',
            class_name='Worker'
        )
