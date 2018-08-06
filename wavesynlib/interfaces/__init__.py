# -*- coding: utf-8 -*-
"""
Created on Fri Aug 08 16:00:43 2014

@author: Feng-cong Li
"""
import platform

from wavesynlib.languagecenter.wavesynscript import ModelNode
from wavesynlib.interfaces.editor.externaleditor import EditorDict



class Interfaces(ModelNode):
    '''The interface node of WaveSyn, which provides several mechanisms for 
communicating with different software applications and hardware devices.
'''
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.os = ModelNode(
            is_lazy=True, 
            module_name='wavesynlib.interfaces.os.modelnode',
            class_name='OperatingSystem')
        
        self.net = ModelNode(
            is_lazy=True,
            module_name='wavesynlib.interfaces.net.modelnode',
            class_name='Net')
        
        self.gpu = ModelNode(
            is_lazy=True,
            module_name='wavesynlib.interfaces.gpu',
            class_name='GPU')
        
        self.dotnet = ModelNode(
            is_lazy=True, 
            module_name='wavesynlib.interfaces.dotnet',
            class_name='DotNet')
        
        self.imagemagick = ModelNode(
            is_lazy=True,
            module_name='wavesynlib.interfaces.imagemagick',
            class_name='ImageMagickNode')
        
        self.editors = EditorDict()
            
        if platform.system().lower() == 'windows':
            # For nodes who can only run on Windows OS. 
            self.msoffice = ModelNode(
                is_lazy=True,
                module_name='wavesynlib.interfaces.msoffice.modelnode',
                class_name='MSOffice'
            )
