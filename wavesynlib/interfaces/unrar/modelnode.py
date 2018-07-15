# -*- coding: utf-8 -*-
"""
Created on Sun Jul 15 17:28:37 2018

@author: Feng-cong Li
"""

import subprocess as sp



def test(path):
    p = sp.Popen(['unrar', 'lta', path], stdout=sp.PIPE, stderr=sp.PIPE)
    outs, errs = p.communicate()
    