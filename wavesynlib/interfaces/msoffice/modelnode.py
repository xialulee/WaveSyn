# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 23:14:19 2016

@author: Feng-cong Li
"""
from __future__ import print_function, division, unicode_literals

from six import string_types

import re
import win32con
from comtypes import client

from wavesynlib.languagecenter.wavesynscript import Scripting, ModelNode, NodeDict
from wavesynlib.languagecenter.designpatterns import Observable

import copy
import json
import os
import time
import win32gui
from ctypes import POINTER, byref, sizeof, memmove, windll
from comtypes.automation import VARIANT, VT_VARIANT, VT_ARRAY, _VariantClear
from comtypes import _safearray, COMError



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
            
            
            
class WordUtils(ModelNode):
    _SIGNATURE_ = 'WaveSyn inserted PSD image.'
    
    
    def __init__(self, *args, **kwargs):
        self.__com_handle = kwargs.pop('com_handle')
        super(WordUtils, self).__init__(*args, **kwargs)
        
    
    @Scripting.printable    
    def insert_psd_image(self, filename, comment='', resize=None, window=None, range_=None):
        from psd_tools import PSDImage
        from PIL import Image
        from tempfile import NamedTemporaryFile
        
        filename = self.root_node.gui.dialogs.support_ask_open_filename(
            filename, 
            filetypes=[('Photoshop Files', ('*.psd',))])    
        if not filename:
            return 
        
        try:
            temp = NamedTemporaryFile(suffix='.png', delete=False)
            # We cannot use the automatic delete mechanism of NamedTemporaryFile
            # since the save method of the following PIL object will call close of temp file
            # which will activate the self-destruction of the temp file. 
            pil_image = PSDImage.load(filename).as_PIL()
            if resize:
                if  isinstance(resize, string_types):
                    if resize[-1] != u'%':
                        raise ValueError('Percentage should end up with "%".')
                    percent = int(resize[:-1])
                    resize = (pil_image.size[0]*percent//100, pil_image.size[1]*percent//100)
                if resize[0]<pil_image.size[0] and resize[1]<pil_image.size[1]:
                    resample = Image.LANCZOS
                else:
                    resample = Image.BICUBIC
                pil_image = pil_image.resize(resize, resample)
            pil_image.save(temp)

            if window is None:
                document = self.__com_handle.ActiveDocument
                inline_shapes = document.InlineShapes
            else:
                winobj = self.__com_handle.Windows[window]
                document = winobj.Document
                inline_shapes = winobj.Selection.InlineShapes
                
            kwargs = {'FileName':temp.name}
            if range_ is not None:
                kwargs['Range'] = range_
            image = inline_shapes.AddPicture(**kwargs)
                
            temp.close()
            doc_dir = self.__com_handle.ActiveDocument.Path
            if doc_dir:
                try:                
                    relative_path = os.path.relpath(filename, doc_dir)
                except ValueError:
                    relative_path = ''
            else:
                relative_path = ''
            image.Title = self._SIGNATURE_
            image.AlternativeText = json.dumps({
                'path':filename, 
                'relative_path':relative_path,
                'time':int(time.time()),
                'resize':resize,
                'comment':comment})
        finally:
            if os.path.exists(temp.name):
                os.remove(temp.name)
                
    
    @Scripting.printable            
    def update_psd_images(self, relative_first=True, window=None):        
        psd_shapes = []
        
        if window is None:
            document = self.__com_handle.ActiveDocument
            inline_shapes = document.InlineShapes
        else:
            winobj = self.__com_handle.Windows[window]
            document = winobj.Document
            inline_shapes = winobj.Selection.InlineShapes        
        
        for shape in inline_shapes:
            try:
                title = shape.Title
            except COMError:
                continue
            if title == self._SIGNATURE_:
                psd_shapes.append(shape)
                
        for shape in psd_shapes:
            info = json.loads(shape.AlternativeText)
            insert_time = info['time']
            file_path = info['path']
            relative_path = info['relative_path']
            comment = info['comment']
            resize = info['resize']
            mtime = os.path.getmtime(file_path)
            if mtime > insert_time:
                rng = shape.Range
                shape.Delete()
                p1 = os.path.abspath(os.path.join(self.__com_handle.ActiveDocument.Path, relative_path))
                p2 = file_path
                if not relative_first:
                    p1, p2 = p2, p1
                if os.path.exists(p1):
                    file_path = p1
                else:
                    file_path = p2
                self.insert_psd_image(file_path, resize=resize, comment=comment, range_=rng)
        

        
class AppObject(ModelNode):    
    def __init__(self, *args, **kwargs):
        com_handle = kwargs.pop('com_handle')
        super(AppObject, self).__init__(self, *args, **kwargs)
        self.__com_handle = com_handle
        
        
    @property
    def name(self):
        raise NotImplementedError
        

    @property
    def com_handle(self):
        return self.__com_handle
        
        
    @property
    def caption(self):
        return self.__com_handle.Caption
        
        
    @Scripting.printable
    def show_window(self, show=True):
        self.com_handle.Visible = show    
        
        
    @Scripting.printable
    def change_caption(self, new_caption):
        self.com_handle.Caption = new_caption
        
        
        
class ExcelObject(AppObject):
    def __init__(self, *args, **kwargs):
        super(ExcelObject, self).__init__(*args, **kwargs)
        self.utils = ExcelUtils(com_handle=self.com_handle)
        
        
    @property
    def name(self):
        return 'Excel'
        
        
    @Scripting.printable
    def set_foreground(self):    
        hwnd = self.com_handle.Hwnd
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        
        
        
class WordObject(AppObject):       
    def __init__(self, *args, **kwargs):
        super(WordObject, self).__init__(*args, **kwargs)
        self.utils = WordUtils(com_handle=self.com_handle)

    @property
    def name(self):
        return 'Word'        
        
    @property
    def windows(self):
        return self.com_handle.Windows
        
        
    @Scripting.printable
    def set_foreground(self, index=None):
        if index:        
            window = self.com_handle.Windows[index]
        else:
            window = self.com_handle.ActiveWindow
        old_caption = window.Caption
        new_caption = 'wavesyn-word-interface-windowfinder-uniq-id-' + str(time.time())
        len_new = len(new_caption)
        try:
            window.Caption = new_caption
            
            def finder(hwnd, param):
                title = win32gui.GetWindowText(hwnd)
                if title[:len_new] == new_caption:
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(hwnd)
                    return False
                else:
                    return True
                    
            try:
                win32gui.EnumWindows(finder, None)
            except:
                pass
        finally:
            window.Caption = old_caption
            
            
            
class WordEventsSink(object):
    def __init__(self, office_dict):
        self.__office_dict = office_dict
    
    
    def ApplicationEvents4_DocumentOpen(self, this, doc):
        self.__office_dict.notify_observers()
        
        
    def ApplicationEvents4_Quit(self, this):
        self.__office_dict.notify_observers()
      


class MSOffice(NodeDict, Observable):
    _prog_info = {
        'word':  {'id':'Word.Application', 'class':WordObject},
        'excel': {'id':'Excel.Application', 'class':ExcelObject}
    }
    
    def __init__(self, *args, **kwargs):
        NodeDict.__init__(self, *args, **kwargs)
        Observable.__init__(self)
        self.__word_events_sink = WordEventsSink(self)
        
        
    def _generate_object(self, app_name, func):
        app_name = app_name.lower()
        com_handle = func(self._prog_info[app_name]['id'])
        
        # Word Application does not have Hwnd property.
        if hasattr(com_handle, 'Hwnd'):
            for id_ in self:
                if hasattr(self[id_].com_handle, 'Hwnd') and self[id_].com_handle.Hwnd == com_handle.Hwnd:
                    return id_
        
        wrapper = self._prog_info[app_name]['class'](com_handle=com_handle)
        wrapper.show_window()
        
        if app_name == 'word':
            # The connection object should be stored, 
            # or it will be gabage collected, and consequently, 
            # event sink will not be notified any more. 
            self.__word_events_connection = client.GetEvents(wrapper.com_handle, self.__word_events_sink)

        object_id = id(wrapper)
        self[object_id] = wrapper
        return object_id
        

    @Scripting.printable        
    def get_active(self, app_name):
        app_name = self.root_node.gui.dialogs.support_ask_list_item(
            app_name,
            the_list=['Word', 'Excel'],
            message='Which app you want to get?'
        )
        app_name = app_name.lower()
        return self._generate_object(app_name, client.GetActiveObject)
        
        
    @Scripting.printable
    def create(self, app_name):
        app_name = self.root_node.gui.dialogs.support_ask_list_item(
            app_name,
            the_list=['Word', 'Excel'],
            message='Which app you want to create?'
        )
        app_name = app_name.lower()
        return self._generate_object(app_name, client.CreateObject)
        
        
        

        