# -*- coding: utf-8 -*-
"""
Created on Sat Sep 28 00:36:34 2019

@author: Feng-cong Li
"""
import os
import tarfile

from wavesynlib.languagecenter.wavesynscript import Scripting, ModelNode, WaveSynScriptAPI



class TarFileManipulator(ModelNode):
    def __init__(self, *args, **kwargs):
        filename = kwargs.pop('filename')
        ModelNode.__init__(self, *args, **kwargs)
        with self.attribute_lock:
            self.filename = filename
            
    @property
    def node_path(self):
        return f'{self.parent_node.node_path}["{self.filename}"]'
        
    @WaveSynScriptAPI
    def extract_all(self, directory):
        directory = self.root_node.gui.dialogs.constant_handler_ASK_DIRECTORY(
            directory, 
            initialdir=os.getcwd())
        if not directory:
            return
            
        tar = tarfile.open(self.filename)
        tar.extractall(directory)

class TarFileManager(ModelNode):
    def __init__(self, *args, **kwargs):
        ModelNode.__init__(self, *args, **kwargs)
        
        
    def __getitem__(self, filename):
        filename = self.root_node.gui.dialogs.constant_handler_ASK_OPEN_FILENAME(
            filename, 
            filetypes=[
                ('TAR Files', ('*.tar', '*.tar.gz', '*.tgz')), 
                ('All Files', '*.*')])
        if not filename:
            return
            
        manipulator = TarFileManipulator(filename=filename)
        object.__setattr__(manipulator, 'parent_node', self)
        manipulator.lock_attribute('parent_node')
        return manipulator
