# -*- coding: utf-8 -*-
"""
Created on Mon Mar 07 16:54:48 2016

@author: Feng-cong Li
"""
from __future__ import print_function, division, unicode_literals

import os
import collections

from six import string_types
from six.moves import xrange

from PyPDF2 import PdfFileReader, PdfFileWriter

from wavesynlib.languagecenter.wavesynscript import ModelNode, Scripting
from wavesynlib.languagecenter.utils import eval_format


class Pages(ModelNode):
    def __init__(self, *args, **kwargs):
        page_index = kwargs.pop('page_index')
        pdf_reader = kwargs.pop('pdf_reader')
        filename = kwargs.pop('filename')
        ModelNode.__init__(self, *args, **kwargs)
        
        self.__single_page = False
                
        
        try:
            page_index = int(page_index)
            self.__range = [page_index]
            self.__single_page = str(page_index)
        except TypeError:
            self.__start = page_index.start if page_index.start else 1
            self.__stop = page_index.stop if page_index.stop else pdf_reader.getNumPages() + 1
            self.__step = page_index.step            
            param = []
            param.append(self.__start)
            param.append(self.__stop)
            if page_index.step:
                param.append(page_index.step)
            self.__range = xrange(*param)
                    
        self.__reader = pdf_reader
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
        for index in self.__range:
            writer.addPage(self.__reader.getPage(index-1))
        with open(filename, 'wb') as output:
            writer.write(output)
            


class PDFFileManipulator(ModelNode):    
    def __init__(self, *args, **kwargs):
        filename = kwargs.pop('filename')
        ModelNode.__init__(self, *args, **kwargs)
        with self.attribute_lock:
            self.filename = filename
        self.__reader = PdfFileReader(filename)

            
    @property
    def node_path(self):
        return eval_format('{self.parent_node.node_path}["{self.filename}"]')

            
    # To Do: This kind of node is short-lived, and need not to notify model_tree_monitor
    # To Do: support ASK_DIALOG
    def __getitem__(self, page_index):
#        if page_index is self.root_node.constants.ASK_DIALOG:
#            user_input = askstring('Page Range', 'Select page range using Python slice syntax "start[:stop[:step]]".\nPage number start from 1.')
#            if not user_input:
#                return
#            user_input = user_input.split(':')
#            user_input = [int(page_num) if page_num else None for page_num in user_input]
#            
#            if len(user_input) == 1:
#                page_index = user_input[0]
#            else:
#                page_index = slice(*user_input)
        page_index = self.root_node.dialogs.support_ask_slice(page_index, 'Page Range', 'Select page range using Python slice syntax "start[:stop[:step]]".\nPage number start from 1.')
        if not page_index:
            return
            
        pages = Pages(page_index=page_index, pdf_reader=self.__reader, filename=self.filename)
        object.__setattr__(pages, 'parent_node', self)
        pages.lock_attribute('parent_node')
        return pages


class PDFFileList(ModelNode):
    def __init__(self, *args, **kwargs):
        self.__file_list = kwargs.pop('file_list')
        ModelNode.__init__(self, *args, **kwargs)
        
    @Scripting.printable
    def merge(self, filename):
        filename = self.root_node.dialogs.support_ask_saveas_filename(
            filename,
            filetypes=[('PDF Files', '*.pdf'), ('All Files', '*.*')],
            defaultextension='.pdf',
            initialdir=os.path.split(self.__file_list[0])[0])
        writer = PdfFileWriter()
        for pdf_filename in self.__file_list:
            reader = PdfFileReader(pdf_filename)
            for k in range(reader.getNumPages()):
                writer.addPage(reader.getPage(k))
        with open(filename, 'wb') as output:
            writer.write(output)


class PDFFileManager(ModelNode):
    def __init__(self, *args, **kwargs):
        ModelNode.__init__(self, *args, **kwargs)
            
    def __getitem__(self, filename):
        dialogs = self.root_node.dialogs
        filename = dialogs.support_ask_open_filename(filename, filetypes=[('PDF Files', '*.pdf'), ('All Files', '*.*')])
        filename = dialogs.support_ask_file_list(filename, filetypes=[('PDF Files', '*.pdf'), ('All Files', '*.*')])
        
        if not filename:
            return
        if isinstance(filename, string_types):
            manipulator = PDFFileManipulator(filename=filename)
            object.__setattr__(manipulator, 'parent_node', self)
            manipulator.lock_attribute('parent_node')
            return manipulator
        elif isinstance(filename, collections.Iterable):
            file_list = PDFFileList(file_list=filename)
            object.__setattr__(file_list, 'parent_node', self)
            file_list.lock_attribute('parent_node')
            return file_list