# -*- coding: utf-8 -*-
"""
Created on Sun Mar 05 20:20:24 2017

@author: Feng-cong Li
"""

from __future__ import print_function, division, unicode_literals

from wavesynlib.languagecenter.wavesynscript import Scripting, ModelNode
from wavesynlib.languagecenter.markdown import utils


class Utils(ModelNode):
    def __init__(self, *args, **kwargs):
        super(Utils, self).__init__(*args, **kwargs)
        
        
    @Scripting.printable
    def generate_table(self, table):
        return utils.generate_table(table)