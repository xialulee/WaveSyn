# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 16:59:26 2015

@author: Feng-cong Li
"""
#import platform
from wavesynlib.languagecenter import htmlutils
from wavesynlib.languagecenter.wavesynscript import ModelNode
from wavesynlib.languagecenter.wavesynscript.modelnode import WaveSynScriptNode

    
class LangCenterNode(ModelNode):
    def __init__(self, *args, **kwargs):
        super(LangCenterNode, self).__init__(*args, **kwargs)
        with self.attribute_lock:
            self.wavesynscript = WaveSynScriptNode()
            self.html_utils = htmlutils.HTMLUtils()
            
                 
#    @Scripting.printable
#    def connectMatlab(self):
#        if platform.system() == 'Windows':
#            from wavesynlib.languagecenter.matlab.modelnode import MatlabServerNode
#            with self.attribute_lock:
#                self.matlab = MatlabServerNode()
#                self.matlab.connectServer()
#        else:
#            raise NotImplementedError('Non-windows OS is not supported.')
            
   

            