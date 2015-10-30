# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 18:24:14 2015

@author: Feng-cong Li
"""

# This is a IPython integration experiment

from wavesynlib.objectmodel import ModelNode
from wavesynlib.common import setMultiAttr, autoSubs, evalFmt, Singleton
from guicomponents.tk import ValueChecker, TaskbarIcon

import os
import thread
from inspect import getsourcefile

from Tkinter import *
from Tix import Tk
import Tix

import numpy



# Scripting Sub-System
class ScriptCode(object):
    def __init__(self, code):
        self.code = code
        
class Scripting(ModelNode):
    _xmlrpcexport_  = []    
    
    rootName = 'wavesyn' # The name of the object model tree's root
    nameSpace = {'locals':{}, 'globals':{}}
    
    @staticmethod
    def paramsToStr(*args, **kwargs):
        def paramToStr(param):
            if isinstance(param, ScriptCode):
                return param.code
            else:
                return repr(param)
                
        strArgs = ', '.join([paramToStr(arg) for arg in args]) if args else ''
        strKwargs = ', '.join([evalFmt('{key}={paramToStr(kwargs[key])}') for key in kwargs]) \
            if kwargs else ''        
       
            
        if strArgs and strKwargs:
            params = ', '.join((strArgs, strKwargs))
        else:
            params = strArgs if strArgs else strKwargs
        return params
        
    def __init__(self, rootNode):
        super(Scripting, self).__init__()
        self.__rootNode = rootNode
            
    def executeFile(self, filename):
        execfile(filename, **self.nameSpace) #?
                
    @staticmethod    
    def printable(method):
        def func(self, *args, **kwargs):
            callerLocals    = sys._getframe(1).f_locals
            #####################################
            #print(method.__name__, True if 'printCode' in callerLocals else False)
            #####################################            
            if 'printCode' in callerLocals and callerLocals['printCode']:
                ret = Application.instance.printAndEval(
                    evalFmt(
                        '{self.nodePath}.{method.__name__}({Scripting.paramsToStr(*args, **kwargs)})'
                    )
                )
            else:                          
                ret = method(self, *args, **kwargs)
            return ret
        func.__doc__    = method.__doc__
        func.__name__   = method.__name__
        return func

                                   
# End Scripting Sub-System



class Application(ModelNode):
    __metaclass__ = Singleton
    
    def __init__(self):
        ModelNode.__init__(self, nodeName='wavesyn', isRoot=True)
        
        from langcenter.scripting import Scripting        
        
        globals()[Scripting.rootName] = self
        
        root = Tk()
        valueChecker = ValueChecker(root)
        filePath    = getsourcefile(type(self))
        dirPath     = os.path.split(filePath)[0]
        
        configFileName  = os.path.join(dirPath, 'config.json')
        
        with self.attributeLock:
            setMultiAttr(self, 
                root = root,
                balloon = Tix.Balloon(root),
                taskbarIcon = TaskbarIcon(root),

                mainThreadId = thread.get_ident(),

                valueChecker = valueChecker,
                checkInt = valueChecker.checkInt,
                checkFloat = valueChecker.checkFloat,
                checkPositiveFloat = valueChecker.checkPositiveFloat,
                
                filePath = filePath,
                dirPath = dirPath,
                configFileName = configFileName
            )
            
        from basewindow import WindowDict
        self.windows = WindowDict()
        
    def createWindow(self, moduleName, className):        
        mod = __import__(autoSubs('toolwindows.$moduleName'), globals(), locals(), [className], -1)
        return self.windows.add(node=getattr(mod, className)())
        
    def printAndEval(self, expr):
        #with self.execThreadLock:
        #self.streamManager.write(expr+'\n', 'HISTORY')
        #ret = eval(expr, Scripting.nameSpace['globals'], Scripting.nameSpace['locals'])
        localVars = locals()
        localVars['r_'] = numpy.r_
        ret = eval(expr, globals(), localVars)
#        if ret != None:
#            self.streamManager.write(str(ret)+'\n', 'RETVAL')
        return ret 

    def notifyWinQuit(self, win):
        #self.printTip(evalFmt('{win.nodePath} is closed, and its ID becomes defunct for scripting system hereafter'))
        self.windows.pop(id(win))         
        
 
import threading
class WaveSynThread(object):
    class Thread(threading.Thread):
        def __init__(self, func):
            self.func   = func
            threading.Thread.__init__(self)
            
        def run(self):
            self.func()
            
    @staticmethod
    def start(func):
        app = Application.instance
        theThread  = WaveSynThread.Thread(func)
        theThread.start()
        while theThread.isAlive():
            app.root.update()
            for winId in app.windows:
                app.windows[winId].update()

   
def uiImagePath(filename):
    return os.path.join(Application.instance.dirPath, 'images', filename)     