# -*- coding: utf-8 -*-
"""
Created on Sun Apr 04 17:19:59 2017

@author: Feng-cong Li
"""
from wavesynlib.languagecenter.wavesynscript import ModelNode



class DotNet(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.zxing = ModelNode(
            is_lazy=True,
            module_name='wavesynlib.interfaces.dotnet.zxing',
            class_name='ZXingNET'
        )
