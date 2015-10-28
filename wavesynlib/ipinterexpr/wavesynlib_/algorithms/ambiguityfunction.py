# -*- coding: utf-8 -*-
"""
Created on Tue Apr 07 10:25:52 2015

@author: Feng-cong Li
"""

from __future__ import division
import numpy as np


def discaf(x, y):
    '''Discrete-Ambiguity Function of vector x and y.'''
    xN      = len(x)
    yN      = len(y)
    caf     = np.zeros((xN, xN+yN-1), dtype=np.complex)
    for p in np.arange(-xN/2, xN/2):
        caf[p+xN/2, :]  = np.correlate(y, x * np.exp(1j * 2 * np.pi * p / xN * np.arange(xN)), 'full')
    return caf