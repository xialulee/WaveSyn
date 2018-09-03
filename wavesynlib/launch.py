# -*- coding: utf-8 -*-
"""
Created on Fri May 23 10:56:05 2014

@author: whhit
"""
import os
import sys

        

wavesyn_directory = os.path.join(os.path.split(__file__)[0], '..')
sys.path.insert(0, wavesyn_directory)

from wavesynlib import application

def main():
    application.mainloop()
    

if __name__ == '__main__':
    main()