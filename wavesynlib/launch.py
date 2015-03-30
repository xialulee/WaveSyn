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
    
    def getPath(self): 
        filePath    = getsourcefile(type(self))
        dirPath     = os.path.split(filePath)[0]
        return os.path.abspath(os.path.join(dirPath, '..'))
        

wavesynPath = WaveSynPath()
sys.path.append(wavesynPath.getPath())
from wavesynlib import application

if __name__ == '__main__':
    application.mainloop()