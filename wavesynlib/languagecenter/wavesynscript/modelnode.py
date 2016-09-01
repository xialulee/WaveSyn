# -*- coding: utf-8 -*-
"""
Created on Sat Aug 27 23:09:18 2016

@author: Feng-cong Li
"""

from __future__ import print_function, division, unicode_literals

from wavesynlib.languagecenter.wavesynscript import (
    ModelNode, Constants, modes
)


class WaveSynScriptNode(ModelNode):
    def __init__(self, *args, **kwargs):
        super(WaveSynScriptNode, self).__init__(*args, **kwargs)
        self.constants = Constants
        self.modes = modes.ModesNode()
            