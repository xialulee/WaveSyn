# -*- coding: utf-8 -*-
"""
Created on Mon Jul 28 15:05:11 2014

@author: xialulee
"""
from Tkinter                         import *
from ttk                             import *
from openpyxl.reader.excel           import load_workbook
from copy                            import copy

from wavesynlib.guicomponents        import ScrolledList
from wavesynlib.languagecenter.utils import MethodDelegator

def selectSheet(workBook, ignoreBlankSheet=True, labelText='Select a sheet'):
    retval  = [0]
    
    sheetNames  = workBook.getSheetNames()
    
    if ignoreBlankSheet:
        sheetNames_backup   = copy(sheetNames)
        for name in sheetNames_backup:
            sheet   = workBook.getSheetByName(name)
            print 'rows:', sheet.get_highest_row()
            if sheet.get_highest_row() == 0:
                sheetNames.remove(name)
                
    if ignoreBlankSheet and len(sheetNames) == 1:
        return sheetNames[0]
    
    win = Toplevel()
    win.resizable(width=False, height=False)
    Label(win, text=labelText).pack()
                
    listBox = ScrolledList(win)
    listBox.pack()
    for name in sheetNames:
        listBox.insert(END, name)
        
    def onClick():
        retval[0]   = listBox.list.get(listBox.curSelection[0])
        win.destroy()
    Button(win, text='OK', command=onClick).pack()
    win.grab_set()
    win.focus_set()
    win.wait_window()
    return retval[0]
    
    
class WorkBook(object):
    methodNameMap   = {
        'getSheetNames':  'get_sheet_names',
        'getSheetByName':    'get_sheet_by_name'
    }
    for methodName in methodNameMap:
        locals()[methodName]    = MethodDelegator('book', methodNameMap[methodName])
        
    def __init__(self, fileName=None):
        if fileName:
            self.load(fileName)
            
    def load(self, fileName):
        self.__fileName = fileName
        self.__book     = load_workbook(fileName)
        
    def getColumn(self, sheetName, columnIdx):
        workSheet   = self.__book.get_sheet_by_name(sheetName)
        return [workSheet.cell(row=rowIdx, column=columnIdx).value for rowIdx in range(1, workSheet.get_highest_row()+1)]
        
    @property
    def book(self):
        return self.__book
            