# -*- coding: utf-8 -*-
"""
Created on Wed Apr 13 17:26:10 2016

@author: Feng-cong Li
"""

import visa

_resource_manager = None

def get_resource_manager():
    global _resource_manager
    if _resource_manager is None:
        try:
            _resource_manager = visa.ResourceManager()
        except:
            _resource_manager = visa.ResourceManager('@py')
    return _resource_manager