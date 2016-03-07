# -*- coding: utf-8 -*-
"""
Created on Mon Mar 07 16:54:48 2016

@author: Feng-cong Li
"""
from __future__ import print_function, division, unicode_literals

from six.moves import xrange
from six.moves.tkinter_tkfiledialog import askopenfilename, asksaveasfilename

from PyPDF2 import PdfFileReader, PdfFileWriter

from wavesynlib.languagecenter.wavesynscript import ModelNode, Scripting
from wavesynlib.languagecenter.utils import eval_format


class Pages(ModelNode):
    def __init__(self, *args, **kwargs):
        page_index = kwargs.pop('page_index')
        pdf_reader = kwargs.pop('pdf_reader')
        ModelNode.__init__(self, *args, **kwargs)
        
        self.__single_page = False
        
        try:
            page_index = int(page_index)
            self.__range = [page_index]
            self.__single_page = str(page_index)
        except TypeError:
            param = []
            param.append(page_index.start)
            param.append(page_index.stop)
            if page_index.step:
                param.append(page_index.step)
            self.__range = xrange(*param)
            
            self.__start = page_index.start
            self.__stop = page_index.stop
            self.__step = page_index.step
        
        self.__reader = pdf_reader
            
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
        if filename is self.root_node.constants.ASK_DIALOG:
            filename = asksaveasfilename(filetypes=[('PDF Files', '*.pdf'), ('All Files', '*.*')])
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
        pages = Pages(page_index=page_index, pdf_reader=self.__reader)
        object.__setattr__(pages, 'parent_node', self)
        pages.lock_attribute('parent_node')
        return pages


class PDFFileManager(ModelNode):
    def __init__(self, *args, **kwargs):
        ModelNode.__init__(self, *args, **kwargs)
            
    def __getitem__(self, filename):
        if filename is self.root_node.constants.ASK_DIALOG:
            filename = askopenfilename(filetypes=[('PDF Files', '*.pdf'), ('All Files', '*.*')])
        if not filename:
            return
        manipulator = PDFFileManipulator(filename=filename)
        object.__setattr__(manipulator, 'parent_node', self)
        manipulator.lock_attribute('parent_node')
        return manipulator