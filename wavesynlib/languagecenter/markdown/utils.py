# -*- coding: utf-8 -*-
"""
Created on Sun Mar 05 20:14:08 2017

@author: Feng-cong Li
"""

from __future__ import print_function, division, unicode_literals



def generate_table(table):
    head = table[0]
    head_code = ''.join(('|'+str(item) for item in head))
    split = '|'.join(['---']*len(head))
    rows = [head_code, split]
    for row in table[1:]:
        rows.append('|'.join([str(item) for item in row]))
    return '\n'.join(rows)
    