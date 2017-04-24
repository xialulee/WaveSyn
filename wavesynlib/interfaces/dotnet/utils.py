# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 22:57:24 2017

@author: Feng-cong Li
"""

from __future__ import print_function, division



def new_and_init(class_object, **kwargs):
    obj = class_object()
    for key in kwargs:
        setattr(obj, key, kwargs[key])
        