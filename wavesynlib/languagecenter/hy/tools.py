# -*- coding: utf-8 -*-
"""
Created on Thu Dec 20 16:36:17 2018

@author: Feng-cong Li
"""

from pathlib import Path



def get_hy_file_dir(path):
    p = Path(path)
    dir_path = p.parent
    if dir_path.parts[-1] == '__pycache__':
        dir_path = dir_path.parent
    return dir_path
