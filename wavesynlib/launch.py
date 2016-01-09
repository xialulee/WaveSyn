# -*- coding: utf-8 -*-
"""
Created on Fri May 23 10:56:05 2014

@author: whhit
"""
import os
import sys
from inspect import getsourcefile

class WaveSynPath(object):
    def __init__(self):
        pass
    
    def get_path(self): 
        file_path    = getsourcefile(type(self))
        dir_path     = os.path.split(file_path)[0]
        return os.path.abspath(os.path.join(dir_path, '..'))
        

wavesynPath = WaveSynPath()
sys.path.insert(0, wavesynPath.get_path())

from wavesynlib import application
wavesyn = application.Application()

if __name__ == '__main__':
    wavesyn.mainloop()