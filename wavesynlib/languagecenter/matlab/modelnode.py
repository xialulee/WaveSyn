# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 16:07:51 2015

@author: Feng-cong Li
"""
from wavesynlib.objectmodel                  import ModelNode
from wavesynlib.languagecenter.wavesynscript import Scripting
import wavesynlib.interfaces.matlab.client   as matlabclient

class MatlabServerNode(ModelNode):
    def __init__(self, *args, **kwargs):
        super(MatlabServerNode, self).__init__(*args, **kwargs)
        self.__server   = None
        
    @Scripting.printable
    def connectServer(self):
        if self.__server is None:
            self.__server   = matlabclient.MatlabCOMServer()
            
    @Scripting.printable
    def releaseServer(self):
        self.__server.release()
        self.__server   = None
        
    @Scripting.printable
    def getVar(self, name, globalVar=False):
        if globalVar:
            return self.__server.nsGlobal[name]
        else:
            return self.__server.nsBase[name]
            
    @Scripting.printable
    def setVar(self, name, value, globalVar=False):
        if globalVar:
            self.__server.nsGlobal[name]    = value
        else:
            self.__server.nsBase[name]      = value