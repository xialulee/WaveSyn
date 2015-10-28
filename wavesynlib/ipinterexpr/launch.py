# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 19:09:54 2015

@author: Feng-cong Li
"""

#from wavesynlib.ipinterexpr.ipyintegratetest import Application
#
#if __name__ == '__main__':
#    app = Application()
#    from IPython.lib.inputhook import enable_gui
#    enable_gui('tk', app.root)
    
    
import os
import sys
from inspect import getsourcefile

class WaveSynPath(object):
    def __init__(self):
        pass
    
    def getPath(self): 
        filePath    = getsourcefile(type(self))
        dirPath     = os.path.split(filePath)[0]
        return os.path.abspath(os.path.join(dirPath, '../..'))
        

wavesynPath = WaveSynPath()
sys.path.insert(0, wavesynPath.getPath())

from wavesynlib_ import application
wavesyn = application.Application()

if __name__ == '__main__':   
    from IPython.lib.inputhook import enable_gui
    enable_gui('tk', wavesyn.root)