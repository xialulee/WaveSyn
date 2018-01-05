# -*- coding: utf-8 -*-
"""
Created on Tue Aug 11 16:01:51 2015

@author: Feng-cong Li
"""
import os
import sys
from pathlib import Path



def winopen(path):
    path = Path(path)
    if path.is_dir():
        os.system('explorer.exe ' + str(path))
    elif path.is_file():
        os.system('explorer.exe /select,' + str(path))
    else:
        raise ValueError('Invalid path.')
        
        
        
if __name__ == '__main__':
    path = sys.argv[1]
    try:
        winopen(path)
        sys.exit(0)
    except ValueError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
