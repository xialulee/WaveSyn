# -*- coding: utf-8 -*-
"""
Created on Tue Aug  7 02:17:32 2018

@author: Feng-cong Li
"""

from wavesynlib.languagecenter.wavesynscript import ModelNode



class Net(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.apnic = ModelNode(
            is_lazy = True,
            module_name='wavesynlib.interfaces.net.apnic.modelnode',
            class_name='APNIC')