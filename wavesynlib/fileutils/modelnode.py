# -*- coding: utf-8 -*-
"""
Created on Sat Sep 28 01:13:49 2019

@author: Feng-cong Li
"""

from io import IOBase
from pathlib import PurePath

from wavesynlib.languagecenter.wavesynscript import Scripting, ModelNode
from wavesynlib.fileutils.tar import TarFileManager



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
        
        
    @Scripting.printable
    def calc_hash(self, file, algorithm):
        from wavesynlib.fileutils import calc_hash
        
        file = self.root_node.gui.dialogs.ask_open_filename(
                file, 
                filetype=[('All Files', '*.*')])
                
        if isinstance(file, (str, PurePath)):
            with open(file, 'rb') as fileobj:
                return calc_hash(fileobj, algorithm)
        elif isinstance(file, IOBase):
            return calc_hash(file, algorithm)
