# -*- coding: utf-8 -*-
"""
Created on Sat Apr 04 10:03:17 2015

@author: Feng-cong Li
"""

import os
import sys
import importlib
import subprocess as sp
import inspect

from Tkinter import *
from ttk import *
from Tkinter import Frame

from wavesynlib.guicomponents.tk import ScrolledTree


class ClassSelector(object):
    def __init__(self, packageName, baseClass, displayBaseClass=False):
        self.__packageName = packageName
        self.__baseClass = baseClass
        self.__displayBaseClass = displayBaseClass
        self.__window = window = Toplevel()
        window.title('Class Selector')
        self.__selectedClassName = ''
        self.__selectedModuleName = ''
        
        self.__tree = tree = ScrolledTree(window)
        tree.pack()
        classes = self.loadModules()
        for package in classes:
            packageNode = tree.insert('', END, text=package)
            for className in classes[package]:
                tree.insert(packageNode, END, text=className, values=package)
                
        buttonFrame = Frame(window)
        buttonFrame.pack()
        def onClick(moduleName, className):
            self.__selectedModuleName   = moduleName
            self.__selectedClassName    = className
            window.destroy()
        cancelBtn = Button(buttonFrame, text='Cancel', command=lambda: onClick('', ''))
        cancelBtn.pack(side=RIGHT)
        okBtn     = Button(
            buttonFrame, 
            text='OK', 
            command=lambda: onClick(
                tree.item(tree.selection(), 'values')[0],
                tree.item(tree.selection(), 'text')
            )
        )
        okBtn.pack(side=RIGHT)
        
    def doModel(self):
        win = self.__window
        win.focus_set()
        win.grab_set()
        win.wait_window() 
        return self.__selectedModuleName, self.__selectedClassName
        
    def loadModules(self):
        retval = {}
        package = importlib.import_module(self.__packageName)
        packagePath = os.path.split(package.__file__)[0]
        for item in os.listdir(packagePath):
            fileName = item.split('.')            
            if fileName[-1] == 'py':
                mod = importlib.import_module('.'.join((self.__packageName, fileName[0])))
                modItemNames = dir(mod)
                for modItemName in modItemNames:
                    modItem = getattr(mod, modItemName)
                    if isinstance(modItem, type) and issubclass(modItem, self.__baseClass):
                        if not self.__displayBaseClass and modItem is self.__baseClass:
                            continue
                        if mod.__name__ not in retval:
                            retval[mod.__name__] = []
                        retval[mod.__name__].append(modItemName)
        return retval
                

def askClassName(packageName, baseClass):
    filePath    = inspect.getsourcefile(ClassSelector)
    p           = sp.Popen(['python', filePath, packageName, baseClass.__module__, baseClass.__name__], stdout=sp.PIPE);
    stdout, stderr  = p.communicate()
    return stdout.strip().split()

        
        
if __name__ == '__main__':
    packageName     = sys.argv[1]
    moduleName      = sys.argv[2]
    baseClassName   = sys.argv[3]
    mod             = importlib.import_module(moduleName)
    baseClassObj    = getattr(mod, baseClassName)
    root = Tk()
    root.withdraw()
    classSel = ClassSelector(packageName, baseClassObj) 
    for s in classSel.doModel():
        print s
    
        
    