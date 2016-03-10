# -*- coding: utf-8 -*-
"""
Created on Mon Mar 07 16:54:48 2016

@author: Feng-cong Li
"""
from __future__ import print_function, division, unicode_literals

import os

from six.moves import xrange

from PyPDF2 import PdfFileReader, PdfFileWriter

from wavesynlib.languagecenter.wavesynscript import ModelNode, FileManager, FileManipulator, FileList, Scripting
from wavesynlib.languagecenter.utils import eval_format


class Pages(ModelNode):
    def __init__(self, *args, **kwargs):
        page_index = kwargs.pop('page_index')
        filename = kwargs.pop('filename')
        ModelNode.__init__(self, *args, **kwargs)
        
        self.__single_page = False
        self.__reader = reader = PdfFileReader(filename)
                        
        try:
            page_index = int(page_index)
            self.__range = [page_index]
            self.__single_page = str(page_index)
        except TypeError:
            # To Do: Support negative indices
            self.__start = page_index.start if page_index.start else 1
            self.__stop = page_index.stop if page_index.stop else reader.getNumPages() + 1
            self.__step = page_index.step            
            param = []
            param.append(self.__start)
            param.append(self.__stop)
            if page_index.step:
                param.append(page_index.step)
            self.__range = xrange(*param)
                    
        self.__filename = filename
            
    @property
    def node_path(self):
        if self.__single_page:
            name = self.__single_page
        elif self.__step:
            name = '{}:{}:{}'.format(self.__start, self.__stop, self.__step)
        else:
            name = '{}:{}'.format(self.__start, self.__stop)
        
        return eval_format('{self.parent_node.node_path}[{name}]')
        
    @Scripting.printable
    def write(self, filename):
        filename = self.root_node.dialogs.support_ask_saveas_filename(
            filename, 
            filetypes=[('PDF Files', '*.pdf'), ('All Files', '*.*')],
            defaultextension='.pdf',
            initialdir=os.path.split(self.__filename)[0])
        if not filename:
            return
        writer = PdfFileWriter()
        reader = self.__reader
        for index in self.__range:
            writer.addPage(reader.getPage(index-1))
        with open(filename, 'wb') as output:
            writer.write(output)
            


class PDFFileManipulator(FileManipulator):    
    def __init__(self, *args, **kwargs):
        FileManipulator.__init__(self, *args, **kwargs)
            
    @property
    def node_path(self):
        return eval_format('{self.parent_node.node_path}["{self.filename}"]')
            
    # To Do: This kind of node is short-lived, and need not to notify model_tree_monitor
    def __getitem__(self, page_index):
        page_index = self.root_node.dialogs.support_ask_slice(page_index, 'Page Range', 'Select page range using Python slice syntax "start[:stop[:step]]".\nPage number start from 1.')
        if not page_index:
            return
            
        pages = Pages(page_index=page_index, filename=self.filename)
        object.__setattr__(pages, 'parent_node', self)
        pages.lock_attribute('parent_node')
        return pages


class PDFFileList(FileList):
    def __init__(self, *args, **kwargs):
        FileList.__init__(self, *args, **kwargs)
        
    @Scripting.printable
    def merge(self, filename):
        filename = self.root_node.dialogs.support_ask_saveas_filename(
            filename,
            filetypes=[('PDF Files', '*.pdf'), ('All Files', '*.*')],
            defaultextension='.pdf',
            initialdir=os.path.split(self.filelist[0])[0])
        if not filename:
            return
        writer = PdfFileWriter()
        for pdf_filename in self.filelist:
            reader = PdfFileReader(pdf_filename)
            for k in range(reader.getNumPages()):
                writer.addPage(reader.getPage(k))
        with open(filename, 'wb') as output:
            writer.write(output)


class PDFFileManager(FileManager):
    def __init__(self, *args, **kwargs):
        kwargs['filetypes'] = [('PDF Files', '*.pdf'), ('All Files', '*.*')]
        kwargs['manipulator_class'] = PDFFileManipulator
        kwargs['list_class'] = PDFFileList
        FileManager.__init__(self, *args, **kwargs)
            
