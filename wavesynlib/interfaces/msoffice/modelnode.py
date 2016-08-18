# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 23:14:19 2016

@author: Feng-cong Li
"""
from __future__ import print_function, division, unicode_literals

import re
from comtypes import client

from wavesynlib.languagecenter.wavesynscript import Scripting, ModelNode, NodeDict


class ExcelCOMObject(ModelNode):
    def __init__(self, *args, **kwargs):
        excel_handle = kwargs.pop('excel_handle')
        super(ExcelCOMObject, self).__init__(*args, **kwargs)
        self.__excel_handle = excel_handle
        self.__regex_for_addr = re.compile('([A-Z]+)([0-9]+)')
        
    def _get_xy(self, addr):
        x_str, y_str = re.match(self.__regex_for_addr, addr).groups()
        y = int(y_str) - 1
        x = 0
        for c in x_str:
            x *= 26
            x += ord(c)-64
        return x-1, y
        
    def _get_addr(self, x, y):
        addr_x = []
        while True:
            addr_x.insert(0, x % 26 - 1)
            x //= 26
            if x == 0: break
        addr_x[-1] += 1
        addr_x_str = ''.join([chr(i+65) for i in addr_x])
        addr_y_str = str(y+1)
        return addr_x_str + addr_y_str
        
    @property
    def excel_handle(self):
        return self.__excel_handle
        
    @Scripting.printable
    def write_range(self, workbook, sheet, up_left, data):
        if workbook.lower() == 'active':
            workbook = self.__excel_handle.ActiveWorkbook
        else:
            workbook = None # To Do: Raise some exception
            
        sheet = workbook.Sheets(sheet)
        
        up_left_x, up_left_y = self._get_xy(up_left)
        
        for m, row in enumerate(data):
            for n, d in enumerate(row):
                sheet.Range(self._get_addr(n+up_left_x, m+up_left_y)).Value[()] = d


class Excel(NodeDict):
    progid = 'Excel.Application'    
    
    def __init__(self, *args, **kwargs):
        super(Excel, self).__init__(*args, **kwargs)
        
    @Scripting.printable
    def get_active_object(self):
        excel_handle = client.GetActiveObject(self.progid)
        wrapper = ExcelCOMObject(excel_handle=excel_handle)
        object_id = id(wrapper)
        self[object_id] = wrapper
        return object_id
        
    
class MSOffice(ModelNode):
    def __init__(self, *args, **kwargs):
        super(MSOffice, self).__init__(*args, **kwargs)
        with self.attribute_lock:
            self.excel = Excel()
        