# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 16:59:26 2015

@author: Feng-cong Li
"""

from wavesynlib.languagecenter.wavesynscript    import Scripting, ModelNode
from wavesynlib.languagecenter.matlab.modelnode import MatlabServerNode 


class LangCenterNode(ModelNode):
    def __init__(self, *args, **kwargs):
        super(LangCenterNode, self).__init__(*args, **kwargs)
        
    @Scripting.printable
    def connectMatlab(self):
        with self.attributeLock:
            self.matlab     = MatlabServerNode()
            self.matlab.connectServer()