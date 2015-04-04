# -*- coding: utf-8 -*-
"""
Created on Sat Apr 04 10:03:17 2015

@author: Feng-cong Li
"""

import os

from Tkinter import *
from ttk import *
#from Tkinter import Frame

from guicomponents.tk import ScrolledTree


class ClassSelector(object):
    def __init__(self, packageName, baseClassName):
        self.__packageName = packageName
        self.__baseClassName = baseClassName
        self.__window = window = Toplevel()
        
        self.__tree = tree = ScrolledTree(window)
        
    def __loadModules(self):
        retval = []
        package = __import__(self.__packageName)
        packagePath = os.path.split(package.__file__)[0]
        for item in os.listdir(packagePath):
            fileName = item.split('.')            
            if fileName[-1] == 'py':
                mod = __import__('.'.join((packageName, fileName[0])))
                modItem = dir(mod)
        
        
        
        
    