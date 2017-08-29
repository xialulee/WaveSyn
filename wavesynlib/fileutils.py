# -*- coding: utf-8 -*-
"""
Created on Sun Aug 28 00:38:46 2016

@author: Feng-cong Li
"""

from __future__ import print_function, division, unicode_literals

import os
import tarfile

from wavesynlib.languagecenter.wavesynscript import Scripting, ModelNode
from wavesynlib.languagecenter.utils import eval_format


class TarFileManipulator(ModelNode):
    def __init__(self, *args, **kwargs):
        filename = kwargs.pop('filename')
        ModelNode.__init__(self, *args, **kwargs)
        with self.attribute_lock:
            self.filename = filename
            
    @property
    def node_path(self):
        return eval_format('{self.parent_node.node_path}["{self.filename}"]')
        
    @Scripting.printable
    def extract_all(self, directory):
        directory = self.root_node.gui.dialogs.ask_directory(
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
        filename = self.root_node.gui.dialogs.ask_open_filename(
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
        

class FileUtils(ModelNode):
    def __init__(self, *args, **kwargs):
        ModelNode.__init__(self, *args, **kwargs)                
        self.pdf_files = ModelNode(
            is_lazy=True, 
            module_name='wavesynlib.interfaces.pdf.modelnode', 
            class_name='PDFFileManager')
        self.touchstone_files = ModelNode(
            is_lazy=True, 
            module_name='wavesynlib.interfaces.devcomm.touchstone.modelnode', 
            class_name='TouchstoneFileManager')
        self.tar_files = ModelNode(is_lazy=True, class_object=TarFileManager)
        