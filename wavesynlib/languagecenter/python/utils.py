# -*- coding: utf-8 -*-
"""
Created on Sat Feb  3 00:51:32 2018

@author: Feng-cong Li
"""
import inspect
from copy import deepcopy

from wavesynlib.languagecenter.datatypes import ModulePath



def get_module_path(obj):
    mod = inspect.getmodule(obj)
    return ModulePath(mod.__name__)
