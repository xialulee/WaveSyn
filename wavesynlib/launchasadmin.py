# -*- coding: utf-8 -*-
"""
Created on Mon Sep  3 18:41:53 2018

@author: Feng-cong Li
"""

# See https://stackoverflow.com/a/41930586.

import ctypes, sys, os



if __name__ == '__main__':
    directory = os.path.split(__file__)[0]
    path = os.path.join(directory, 'launch.py')
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, path, None, 1)