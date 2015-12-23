# -*- coding: utf-8 -*-
"""
Created on Wed Dec 23 23:09:57 2015

@author: Feng-cong Li
"""
from __future__ import print_function

import sys

import ctypes
from ctypes import wintypes

def main(argv):
    dllName     = argv[1]
    funcName    = argv[2]
    
    argList     = []
    for arg in argv[3:]:
        value, tp   = arg.split(':')
        tp          = getattr(wintypes, tp)
        obj         = tp()
        obj.value   = type(obj.value)(value)
        argList.append(obj)        

    if hasattr(ctypes.windll, dllName):
        dll     = getattr(ctypes.windll, dllName)
    else:
        dll     = ctypes.windll.LoadLibrary(dllName)
            
    getattr(dll, funcName)(*argList)
    
if __name__ == '__main__':
    sys.exit(main(sys.argv))
    