# -*- coding: utf-8 -*-
"""
Created on Sun Apr 04 17:19:59 2017

@author: Feng-cong Li
"""

from __future__ import print_function, division, unicode_literals

from wavesynlib.languagecenter.wavesynscript import ModelNode

import clr
from six.moves import cStringIO as StringIO



class DotNet(ModelNode):
    def __init__(self, *args, **kwargs):
        super(DotNet, self).__init__(*args, **kwargs)
        
        self.zxing = ModelNode(
            is_lazy=True,
            module_name='wavesynlib.interfaces.dotnet.zxing',
            class_name='ZXingNET'
        )
