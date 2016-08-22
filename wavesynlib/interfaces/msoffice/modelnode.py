# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 23:14:19 2016

@author: Feng-cong Li
"""
from __future__ import print_function, division, unicode_literals

import re
from comtypes import client

from wavesynlib.languagecenter.wavesynscript import Scripting, ModelNode, NodeDict


from ctypes import POINTER, byref, sizeof, memmove
from comtypes.automation import VARIANT, VT_VARIANT, VT_ARRAY, _VariantClear
from comtypes import _safearray


def _set_variant_matrix(variant, value):
    num_row = num_col = None

    if isinstance(value, (list, tuple)) and \
        len(value)>0 and \
        isinstance(value[0], (list, tuple)):
        num_col = len(value[0])
        num_row = len(value)
        for m in range(1, num_row):
            if len(value[m]) != num_col:
                raise TypeError('Input data is not a matrix')
        num_row = len(value)
    
    _VariantClear(variant) # Clear the original data
    rgsa = (_safearray.SAFEARRAYBOUND * 2)()
    rgsa[0].cElements = num_row
    rgsa[0].lBound = 0
    rgsa[1].cElements = num_col
    rgsa[1].lBound = 0
                                            
    pa = _safearray.SafeArrayCreateEx(VT_VARIANT,
                                      2,
                                      rgsa,  # rgsaBound
                                      None)  # pvExtra
                                            
                                            
    if not pa:
        raise MemoryError()

    ptr = POINTER(VARIANT)()  # container for the values
    _safearray.SafeArrayAccessData(pa, byref(ptr))
    try:
        # I have no idea why 2D safearray is column-major.                
        index = 0
        for n in range(num_col):            
            for m in range(num_row):            
                ptr[index] = value[m][n]
                index += 1
    finally:
        _safearray.SafeArrayUnaccessData(pa)
    
    memmove(byref(variant._), byref(pa), sizeof(pa))  
    variant.vt = VT_ARRAY | VT_VARIANT


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
    def object_handle(self):
        return self.__excel_handle
        
    @Scripting.printable
    def write_range(self, workbook, sheet, up_left, data):
        if workbook.lower() == 'active':
            workbook = self.__excel_handle.ActiveWorkbook
        else:
            workbook = None # To Do: Raise some exception
            
        sheet = workbook.Sheets(sheet)
        
        up_left_x, up_left_y = self._get_xy(up_left)
        
        if isinstance(data, (list, tuple)):
            if isinstance(data[0], (list, tuple)): # Nested list or tuple
                row_num = len(data)
                col_num = len(data[0])
                variant = VARIANT()
                try: # Matrix in the form of nested list or tuple
                    _set_variant_matrix(variant, data)
                    sheet.Range(self._get_addr(up_left_x, up_left_y),
                                self._get_addr(up_left_x+col_num-1, up_left_y+row_num-1)).Value[:] = variant
                except TypeError: # Ragged Array
                    for m, row in enumerate(data):
                        sheet.Range(self._get_addr(up_left_x, up_left_y+m),
                                    self._get_addr(up_left_x+len(row)-1, up_left_y+m)).Value[:] = row
            else: # 1D data
                list_len = len(data)
                sheet.Range(self._get_addr(up_left_x, up_left_y), 
                            self._get_addr(up_left_x+list_len-1, up_left_y)).Value[:] = data


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
        