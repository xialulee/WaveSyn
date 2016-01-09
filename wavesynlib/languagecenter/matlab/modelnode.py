# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 16:07:51 2015

@author: Feng-cong Li
"""
from wavesynlib.languagecenter.wavesynscript import Scripting, ModelNode
import wavesynlib.interfaces.matlab.client   as matlabclient
import wavesynlib.interfaces.matlab.mupad    as mupadtypes
import mupad

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
            return self.__server.global_namespace[name]
        else:
            return self.__server.base_namespace[name]
            
    @Scripting.printable
    def setVar(self, name, value, globalVar=False):
        if globalVar:
            self.__server.global_namespace[name]    = value
        else:
            self.__server.base_namespace[name]      = value
            
    @Scripting.printable
    def mupadSymToScipy(self, symName):
        if isinstance(symName, str):
            tree, var   = self.__server.getMuPadExprTree(symName)
        elif isinstance(symName, mupadtypes.Expression):
            tree, var   = symName.tree, symName.variables
        varList     = mupad.varListStrToSymList(var)
        treeList    = mupad.exprTreeStrToSymList(tree)
        return mupad.symListToScipy(treeList, varList)