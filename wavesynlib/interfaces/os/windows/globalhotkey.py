# -*- coding: utf-8 -*-
"""
Created on Sat Nov 24 00:34:39 2018

@author: Feng-cong Li
"""

from copy import deepcopy

from wavesynlib.languagecenter.wavesynscript import ModelNode



class GlobalHotkeyManager(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__hotkey_info = {}
        
        
    def __thread_func(self):
        pass
        
        
    @property
    def hotkey_info(self):
        return deepcopy(self.__hotkey_info)
        
        
    def register(self, modifiers, vk):
        pass
    
    
    def unregister(self, modifiers=None, vk=None, id_=None):
        pass