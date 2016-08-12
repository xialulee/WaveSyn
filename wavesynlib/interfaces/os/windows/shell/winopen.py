# -*- coding: utf-8 -*-
"""
Created on Tue Aug 11 16:01:51 2015

@author: Feng-cong Li
"""
from __future__ import print_function
import os
import sys

def winopen(path):
    if os.path.isdir(path):
        os.system('explorer.exe ' + path)
    elif os.path.isfile(path):
        os.system('explorer.exe /select,' + path)
    else:
        raise ValueError('Invalid path.')
        
if __name__ == '__main__':
    path = sys.argv[1]
    try:
        winopen(path)
        sys.exit(0)
    except ValueError(e):
        print(e, file=sys.stderr)
        sys.exit(1)
