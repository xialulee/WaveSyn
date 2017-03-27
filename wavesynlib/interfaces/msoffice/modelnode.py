# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 23:14:19 2016

@author: Feng-cong Li
"""
from __future__ import print_function, division, unicode_literals

import re
from comtypes import client

from wavesynlib.languagecenter.wavesynscript import Scripting, ModelNode, NodeDict

import copy
from ctypes import POINTER, byref, sizeof, memmove
from comtypes.automation import VARIANT, VT_VARIANT, VT_ARRAY, _VariantClear
from comtypes import _safearray



class BaseObject(ModelNode):
    def __init__(self, *args, **kwargs):
        com_handle = kwargs.pop('com_handle')
        super(BaseObject, self).__init__(self, *args, **kwargs)
        self.__com_handle = com_handle
        
    
    @property
    def com_handle(self):
        return self.__com_handle
        
        
    @Scripting.printable
    def show_window(self, show=True):
        self.com_handle.Visible = show



class ExcelUtils(ModelNode):
    def __init__(self, *args, **kwargs):
        self.__com_handle = kwargs.pop('com_handle')
        super(ExcelUtils, self).__init__(*args, **kwargs)
        self.__regex_for_addr = re.compile('([A-Z]+)([0-9]+)')
        

    @Scripting.printable
    def is_nested_iterable(self, data):
        if isinstance(data, (list, tuple)) and \
            len(data)>0 and \
            isinstance(data[0], (list, tuple)):
            return True
        else:
            return False
            
            
    @Scripting.printable
    def is_ragged(self, data):
        if not self.is_nested_iterable(data):
            raise TypeError('Input data is not a nested list/tuple.')
            
        num_col = len(data[0])
        num_row = len(data)
        for m in range(1, num_row):
            if len(data[m]) != num_col:
                return True        
        return False
        

    @Scripting.printable
    def set_variant_matrix(self, value):
        if not self.is_nested_iterable(value):
            raise TypeError('Input data is not nested list/tuple.')
            
        if self.is_ragged(value):
            raise TypeError('Input data should not be a ragged array.')
            
        num_row = len(value)
        num_col = len(value[0])
        
        variant = VARIANT()
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
        return variant
        
       
    @Scripting.printable
    def transpose(self, data):
        if not self.is_nested_iterable(data):
            if isinstance(data, (list, tuple)): # 1D data
                return [[c] for c in data]
            else:
                raise TypeError('Input data is not nested list/tuple.')
            
        if self.is_ragged(data):
            raise TypeError('Ragged array is not supported.')
            
        num_row = len(data)
        num_col = len(data[0])
        
        return [[data[m][n] for m in range(num_row)] for n in range(num_col)]
        
        
    @Scripting.printable
    def fliplr(self, data):
        if self.is_nested_iterable(data): # 2D data
            retval = copy.deepcopy(data)
            for row in retval:
                row.reverse()
            return retval
        else: 
            if isinstance(data, (list, tuple)): # 1D data
                retval = copy.deepcopy(data)
                retval.reverse()
                return retval
            else:
                raise TypeError('Incompatible data type.')
                
                
    @Scripting.printable
    def flipud(self, data):
        if self.is_nested_iterable(data):
            retval = copy.deepcopy(data)
            retval.reverse()
            return retval
        else: # 1D list/tuple is a row vector.
            raise TypeError('Incompatible data type.')
            
            
    @Scripting.printable
    def replace_string(self, data, old, new):
        if self.is_nested_iterable(data): # 2D Data
            for row in data:
                for index, cell in enumerate(row):
                    row[index] = cell.replace(old, new)
        else:
            if isinstance(data, (list, tuple)): # 1D data
                for index, cell in enumerate(data):
                    data[index] = cell.replace(old, new)
            else:
                raise TypeError('Incompatible data type.')
                
                
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
                
                
    @Scripting.printable 
    def write_range(self, data, top_left, workbook=None, sheet=None):
        if workbook is None:
            workbook = self.__com_handle.ActiveWorkbook
        else:
            workbook = self.__com_handle.Workbooks[workbook]
            
        if sheet is None:
            sheet = workbook.ActiveSheet
        else:
            sheet = workbook.Sheets(sheet)
        
        top_left_x, top_left_y = self._get_xy(top_left)
        
        if not self.is_nested_iterable(data): # 1D data or incompatible data type.
            if isinstance(data, (list, tuple)): # 1D data
                list_len = len(data)
                sheet.Range(self._get_addr(top_left_x, top_left_y), 
                            self._get_addr(top_left_x+list_len-1, top_left_y)).Value[:] = data
                return
            else: # Incomplete data types. 
                raise TypeError('Input data is not nested list/tuple.')
            
        if self.is_ragged(data):
            for m, row in enumerate(data):
                sheet.Range(self._get_addr(top_left_x, top_left_y+m),
                            self._get_addr(top_left_x+len(row)-1, top_left_y+m)).Value[:] = row
            return
        else: # Regular matrix
            row_num = len(data)
            col_num = len(data[0])
            variant = self.set_variant_matrix(data)
            sheet.Range(self._get_addr(top_left_x, top_left_y),
                        self._get_addr(top_left_x+col_num-1, top_left_y+row_num-1)).Value[:] = variant
            return                



class ExcelObject(BaseObject):
    def __init__(self, *args, **kwargs):
        super(ExcelObject, self).__init__(*args, **kwargs)
        self.utils = ExcelUtils(com_handle=self.com_handle)        
        


class WordObject(BaseObject):
    def __init__(self, *args, **kwargs):
        super(WordObject, self).__init__(self, *args, **kwargs)
      


class MSOffice(NodeDict):
    _prog_info = {
        'word':  {'id':'Word.Application', 'class': WordObject},
        'excel': {'id':'Excel.Application', 'class': ExcelObject}
    }
    
    def __init__(self, *args, **kwargs):
        super(MSOffice, self).__init__(*args, **kwargs)
        
        
    def _generate_object(self, prog_name, func):
        prog_name = prog_name.lower()
        com_handle = func(self._prog_info[prog_name]['id'])
        wrapper = self._prog_info[prog_name]['class'](com_handle=com_handle)
        wrapper.show_window()
        object_id = id(wrapper)
        self[object_id] = wrapper
        return object_id
        

    @Scripting.printable        
    def get_active(self, name):
        return self._generate_object(name, client.GetActiveObject)
        
        
    @Scripting.printable
    def create(self, name):
        return self._generate_object(name, client.CreateObject)
        
        
        

        