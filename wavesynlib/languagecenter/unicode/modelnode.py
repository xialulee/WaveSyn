# -*- coding: utf-8 -*-
"""
Created on Wed May 29 13:37:26 2019

@author: Feng-cong Li
"""
from wavesynlib.languagecenter.wavesynscript import ModelNode

from .utils import decorate_text


class UnicodeUtils(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
    def decorate_text(self, text: str, arg: str) -> str:
        return decorate_text(text, arg)
        