# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 16:59:26 2015

@author: Feng-cong Li
"""
#import platform
import wavesynlib.languagecenter.html.modelnode as html_nodes
import wavesynlib.languagecenter.markdown.modelnode as markdown_nodes
from wavesynlib.languagecenter.wavesynscript import ModelNode
from wavesynlib.languagecenter.wavesynscript.modelnode import WaveSynScriptNode

    
class LangCenterNode(ModelNode):
    def __init__(self, *args, **kwargs):
        super(LangCenterNode, self).__init__(*args, **kwargs)
        self.wavesynscript = WaveSynScriptNode()
        self.html_utils = html_nodes.Utils()
        self.markdown_utils = markdown_nodes.Utils()
