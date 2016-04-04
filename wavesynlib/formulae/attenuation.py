# -*- coding: utf-8 -*-
"""
Created on Mon Apr 04 16:35:08 2016

@author: Feng-cong Li
"""
from __future__ import print_function, division, unicode_literals

import collections
import itertools
import math

import numpy as np


def free_space_loss(freq, dist):
    if not isinstance(freq, collections.Iterable):
        freq = [freq]
    if not isinstance(dist, collections.Iterable):
        dist = [dist]
        
    result = []
    for f, d in itertools.product(freq, dist):
        att = 36.6 + 20*math.log10(f/1e6*d/1.6093)
        result.append((f, d, att))
        
    return result
    
    
if __name__ == '__main__':
    freq = np.r_[10:101] * 1e9
    result = free_space_loss(freq, 1)
    for f, d, att in result:
        print(f, d, att)
        