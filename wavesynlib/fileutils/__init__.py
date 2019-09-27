# -*- coding: utf-8 -*-
"""
Created on Sun Aug 28 00:38:46 2016

@author: Feng-cong Li
"""

import hashlib



def calc_hash(fileobj, algorithm):
    m = getattr(hashlib, algorithm.lower())()
    while True:
        data = fileobj.read(1048576)
        if not data:
            break
        m.update(data)
    return m.hexdigest()
