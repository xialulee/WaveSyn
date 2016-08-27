# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 16:59:26 2015

@author: Feng-cong Li
"""
#import platform
from wavesynlib.languagecenter import htmlutils
from wavesynlib.languagecenter.wavesynscript import ModelNode
from wavesynlib.languagecenter.wavesynscript.modelnode import WaveSynScriptNode

    
class LangCenterNode(ModelNode):
    def __init__(self, *args, **kwargs):
        super(LangCenterNode, self).__init__(*args, **kwargs)
        self.wavesynscript = WaveSynScriptNode()
        self.html_utils = htmlutils.HTMLUtils()
