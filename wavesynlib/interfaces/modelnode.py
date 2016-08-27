# -*- coding: utf-8 -*-
"""
Created on Tue Aug 23 17:15:07 2016

@author: Feng-cong Li
"""

from __future__ import print_function, division, unicode_literals

import platform

from wavesynlib.languagecenter.wavesynscript import ModelNode
from wavesynlib.interfaces.msoffice.modelnode import MSOffice
from wavesynlib.interfaces.os.modelnode import OperatingSystem


class Interfaces(ModelNode):
    def __init__(self, *args, **kwargs):
        super(Interfaces, self).__init__(*args, **kwargs)
        
        self.os = OperatingSystem()
            
        if platform.system().lower() == 'windows':
            self.msoffice = MSOffice()
