# -*- coding: utf-8 -*-
"""
Created on Fri Aug 08 16:00:43 2014

@author: Feng-cong Li
"""

from __future__ import print_function, division, unicode_literals

import platform

from wavesynlib.languagecenter.wavesynscript import ModelNode



class Interfaces(ModelNode):
    def __init__(self, *args, **kwargs):
        super(Interfaces, self).__init__(*args, **kwargs)
        
        self.os = ModelNode(
            is_lazy=True, 
            module_name='wavesynlib.interfaces.os.modelnode',
            class_name='OperatingSystem'
        )
        
        self.gpu = ModelNode(
            is_lazy=True,
            module_name='wavesynlib.interfaces.gpu',
            class_name='GPU'
        )
        
        self.dotnet = ModelNode(
            is_lazy=True, 
            module_name='wavesynlib.interfaces.dotnet',
            class_name='DotNet'
        )
            
        if platform.system().lower() == 'windows':
            # For nodes who can only run on Windows OS. 
            self.msoffice = ModelNode(
                is_lazy=True,
                module_name='wavesynlib.interfaces.msoffice.modelnode',
                class_name='MSOffice'
            )
