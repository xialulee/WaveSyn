# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 23:14:19 2016

@author: Feng-cong Li
"""

import re
import copy
import json
import os
import time
import win32gui
import win32con
from pathlib import Path
from PIL import Image
from ctypes import POINTER, byref, sizeof, memmove

import pandas as pd

from comtypes import client, _safearray, COMError
from comtypes.automation import VARIANT, VT_VARIANT, VT_ARRAY, _VariantClear

from wavesynlib.languagecenter.wavesynscript import (
    Scripting, ModelNode, WaveSynScriptAPI, NodeDict, code_printer)
from wavesynlib.languagecenter.designpatterns import Observable
from wavesynlib.fileutils.photoshop.psd import get_pil_image


_xlXYScatter = -4169



class ExcelUtils(ModelNode):
    def __init__(self, *args, **kwargs):
        self.__com_handle = kwargs.pop('com_handle')
        super().__init__(*args, **kwargs)
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


    def _get_workbook(self, workbook=None):
        if workbook is None:
            workbook = self.__com_handle.ActiveWorkbook
        else:
            workbook = self.__com_handle.Workbooks[workbook]
        return workbook


    def _get_sheet(self, workbook, sheet=None):
        if sheet is None:
            sheet = workbook.ActiveSheet
        else:
            sheet = workbook.Sheets(sheet)
        return sheet
        

    @WaveSynScriptAPI
    def is_nested_iterable(self, data):
        if isinstance(data, (list, tuple)) and \
            len(data)>0 and \
            isinstance(data[0], (list, tuple)):
            return True
        else:
            return False
            
            
    @WaveSynScriptAPI
    def is_ragged(self, data):
        if not self.is_nested_iterable(data):
            raise TypeError('Input data is not a nested list/tuple.')
            
        num_col = len(data[0])
        num_row = len(data)
        for m in range(1, num_row):
            if len(data[m]) != num_col:
                return True        
        return False
        

    @WaveSynScriptAPI
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
                                                
        pa = _safearray.SafeArrayCreateEx(
            VT_VARIANT,
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
        

    @WaveSynScriptAPI
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
        
        
    @WaveSynScriptAPI
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
                
                
    @WaveSynScriptAPI
    def flipud(self, data):
        if self.is_nested_iterable(data):
            retval = copy.deepcopy(data)
            retval.reverse()
            return retval
        else: # 1D list/tuple is a row vector.
            raise TypeError('Incompatible data type.')
            
            
    @WaveSynScriptAPI
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
                
                
                
                
    @WaveSynScriptAPI 
    def write_range(self, data, top_left, workbook=None, sheet=None):
        workbook = self._get_workbook(workbook)
        sheet = self._get_sheet(workbook, sheet)
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
        
        
    @WaveSynScriptAPI
    def read_range(self, 
        top_left, 
        bottom_right, 
        workbook=None, 
        sheet=None,
        return_dataframe=False,
        column_labels=None):
            
        workbook = self._get_workbook(workbook)
        sheet = self._get_sheet(workbook, sheet)
        
        tl_x, tl_y = self._get_xy(top_left)  
        br_x, br_y = self._get_xy(bottom_right)
        
        rng = sheet.Range(
                self._get_addr(tl_x, tl_y), 
                self._get_addr(br_x, br_y)).Value[:]

        if return_dataframe:
            if not column_labels:
                column_labels = rng[0]
                rng = rng[1:]
            import pandas
            rng = pandas.DataFrame(list(rng), columns=column_labels)

        return rng


    @WaveSynScriptAPI
    def add_xyxy_scatter_chart(self, top_left, bottom_right, workbook=None, sheet=None):
        workbook = self._get_workbook(workbook)
        sheet = self._get_sheet(workbook, sheet)
        sheet.Shapes.AddChart2(-1, _xlXYScatter).Select()
        chart = self.__com_handle.ActiveChart
        sc = chart.SeriesCollection()
        fsc = chart.FullSeriesCollection()

        x_min, y_min = self._get_xy(top_left)
        x_max, y_max = self._get_xy(bottom_right)

        for counter, col_idx in enumerate(range(x_min, x_max+1-x_min, 2)):
            sc.NewSeries()
            coord_x_start = self._get_addr(col_idx, y_min)
            coord_x_stop  = self._get_addr(col_idx, y_max)
            coord_y_start = self._get_addr(col_idx+1, y_min)
            coord_y_stop  = self._get_addr(col_idx+1, y_max)
            # The index of FullSeriesCollection is starting from one rather than zero. 
            fsc[counter+1].XValues = f"{sheet.Name}!{coord_x_start}:{coord_x_stop}"
            fsc[counter+1].Values =  f"{sheet.Name}!{coord_y_start}:{coord_y_stop}"

        
    @WaveSynScriptAPI
    def browser_fill_by_id(
        self, driver, ids, top_left, bottom_right, 
        workbook=None, sheet=None):
        data = self.read_range(top_left, bottom_right, workbook, sheet)
        for id_row, data_row in zip(ids, data):
            for id_, item in zip(id_row, data_row):
                driver.find_element_by_id(id_).send_keys(str(item))
            
            
            
class WordUtils(ModelNode):
    _SIGNATURE_ = 'WaveSyn inserted PSD image.'
    
    
    def __init__(self, *args, **kwargs):
        self.__com_handle = kwargs.pop('com_handle')
        super().__init__(*args, **kwargs)


    def __get_document(self, window=None):
        if window is None:
            return self.__com_handle.ActiveDocument
        else:
            return self.__com_handle.Windows[window].Document
        
    
    @WaveSynScriptAPI    
    def insert_psd_image(self, 
        filename, 
        comment='', 
        resize=None, 
        window=None, 
        range_=None,
        width=None,
        height=None):
        from tempfile import NamedTemporaryFile
        
        filename = self.root_node.gui.dialogs.constant_handler_ASK_OPEN_FILENAME(
            filename, 
            filetypes=[('Photoshop Files', ('*.psd',))])    
        if not filename:
            return 
        
        try:
            temp = NamedTemporaryFile(suffix='.png', delete=False)
            # We cannot use the automatic delete mechanism of NamedTemporaryFile
            # since the save method of the following PIL object will call close of temp file
            # which will activate the self-destruction of the temp file. 
            with open(filename, "rb") as psd_file:
                pil_image = get_pil_image(psd_file, read_channels="min")[0]
            if resize:
                if  isinstance(resize, str):
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
                'path':str(filename), 
                'relative_path':str(relative_path),
                'time':int(time.time()),
                'resize':resize,
                'comment':comment})
            if width:
                image.Width = width
            if height:
                image.Height = height
        finally:
            if os.path.exists(temp.name):
                os.remove(temp.name)
                
    
    @WaveSynScriptAPI            
    def update_psd_images(self, relative_first=True, window=None):        
        psd_shapes = []
        
        if window is None:
            document = self.__com_handle.ActiveDocument
            inline_shapes = document.InlineShapes
        else:
            winobj = self.__com_handle.Windows[window]
            document = winobj.Document
            inline_shapes = document.InlineShapes        
        
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
            
            # Get psd file path. 
            # The alt text of every image inserted by self.insert_psd_image 
            # contains the abspath and relpath of the file.
            # If relative_first is True, 
            #   the procedure will check the availability of the relpath;
            # else,
            #   it will check the abspath first. 
            # Finally, the first available path will be the file_path below.             
            p1 = (Path(document.Path)/relative_path).absolute()
            p2 = Path(file_path)
            if not relative_first:
                p1, p2 = p2, p1
            if p1.exists():
                file_path = p1
            else:
                file_path = p2            

            if not file_path.exists():
                raise IOError(f'PSD file "{p1}" and "{p2}" not exists.')
                
            mtime = file_path.stat().st_mtime
            if mtime > insert_time:
                rng = shape.Range
                width, height = shape.Width, shape.Height
                shape.Delete()
                self.insert_psd_image(
                    file_path, 
                    resize=resize, 
                    comment=comment, 
                    range_=rng,
                    width=width,
                    height=height)
                
                
    @WaveSynScriptAPI
    def adjust_mtdisplayequation_tabs(self, window=None):
        wdAlignTabCenter = 1
        wdTabLeaderSpaces = 0
        wdAlignTabRight = 2
        
        if window is None:
            doc = self.__com_handle.ActiveDocument     
            page_setup = doc.PageSetup
        else:
            doc = self.__com_handle.Windows[window].Document
            page_setup = doc.PageSetup
            
        available_width = page_setup.TextColumns[1]
        
        tab_stops = doc.Styles['MTDisplayEquation'].ParagraphFormat.TabStops
        tab_stops.ClearAll()
        tab_stops.Add(
            Position = available_width / 2,
            Alignment = wdAlignTabCenter,
            Leader = wdTabLeaderSpaces)
        tab_stops.Add(
            Position = available_width,
            Alignment = wdAlignTabRight,
            Leader = wdTabLeaderSpaces)


    @WaveSynScriptAPI
    def get_links_of_shapes(self, window=None):
        doc = self.__get_document(window=window)
        result = []

        def get_link_fullname(shape_coll, index):
            link = shape_coll[index].LinkFormat 
            if link is not None:
                return link.SourceFullName
            else:
                return None

        for name, obj in [("Shape", doc.Shapes), ("InlineShape", doc.InlineShapes)]:
            for index in range(1, obj.Count+1):
                fullname = get_link_fullname(obj, index)
                if fullname:
                    fullname = Path(fullname)
                    result.append(dict(type=name, index=index, source=fullname, exists=fullname.exists()))

        return pd.DataFrame(result)


    @WaveSynScriptAPI
    def fix_links_of_shapes(self, old_root, new_root=0, only_not_exist=False, window=None):
        """Fix links of Shapes and InlineShapes if the relative structure of the linked files is not changed."""
        doc = self.__get_document(window=window)
        directory = Path(doc.Path)
        if isinstance(new_root, int):
            while new_root > 0:
                directory = directory.parent
            new_root = directory
        elif isinstance(new_root, str):
            new_root = Path(new_root)

        links = self.get_links_of_shapes(window=window)

        result = []

        for rowindex, row in links.iterrows():
            source = row["source"]
            if only_not_exist and row["exists"]:
                continue
            relative = source.relative_to(old_root)
            absolute = new_root / relative
            shape_coll = doc.Shapes if row["type"]=="Shape" else doc.InlineShapes
            shape_coll[row["index"]].LinkFormat.SourceFullName = str(absolute)
            result.append(dict(type=row["type"], index=row["index"], old_source=source, new_source=absolute))
        
        return pd.DataFrame(result)



        
class AppObject(ModelNode):    
    def __init__(self, *args, **kwargs):
        com_handle = kwargs.pop('com_handle')
        super().__init__(self, *args, **kwargs)
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
        
        
    @WaveSynScriptAPI
    def show_window(self, show=True):
        self.com_handle.Visible = show    
        
        
    @WaveSynScriptAPI
    def change_caption(self, new_caption):
        self.com_handle.Caption = new_caption

        
    @WaveSynScriptAPI
    def run_macro(self, macro_name, *args):
        self.com_handle.run(macro_name, *args)  
        
        
    @WaveSynScriptAPI
    def foreground_run_macro(self, macro_name, *args):
        self.set_foreground()
        with code_printer(False):
            ret = self.run_macro(macro_name, *args)
        return ret


    def set_foreground(self):
        raise NotImplementedError()        
        
        
        
class ExcelObject(AppObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.utils = ExcelUtils(com_handle=self.com_handle)
        
        
    @property
    def name(self):
        return 'Excel'
        
        
    @WaveSynScriptAPI
    def set_foreground(self):    
        hwnd = self.com_handle.Hwnd
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        
        
        
class WordDocumentObject:
    def __init__(self, parent, handle):
        self.com_handle = handle
        self._event_connection = None
        self.parent = parent
        
        
    def DocumentEvents2_Close(self, this):
        self.parent.DocumentEvents2_Close(this, doc_wrapper=self)
        
        
        
class WordObject(AppObject):       
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.utils = WordUtils(com_handle=self.com_handle)
        self.__event_connection = None
        self._doc_list = []


    @property
    def name(self):
        return 'Word'        

        
    @property
    def windows(self):
        return self.com_handle.Windows
        
        
    @property
    def _event_connection(self):
        return self.__event_connection
        
        
    @_event_connection.setter
    def _event_connection(self, connection):
        self.__event_connection = connection
        
        
    @WaveSynScriptAPI
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
            
            
    @WaveSynScriptAPI
    def open(self, filename):
        self.com_handle.Documents.Open(filename)
        
        
    @WaveSynScriptAPI
    def close_active_document(self):
        self.com_handle.ActiveDocument.Close()
            
                      
    def ApplicationEvents4_DocumentOpen(self, this, doc):
        self.parent_node.notify_observers(
                app='Word', 
                source='Application', 
                event='DocumentOpen', 
                doc=doc)
    
        
        
    def ApplicationEvents4_NewDocument(self, this, doc):            
        for doc_idx in range(self.com_handle.Documents.Count):
            idx1 = doc_idx+1
            if self.com_handle.Documents.Item(idx1) == doc:
                doc = self.com_handle.Documents.Item(idx1)
                doc_wrapper = WordDocumentObject(parent=self, handle=doc)
                doc_wrapper._event_connection = client.GetEvents(doc, doc_wrapper)
                self._doc_list.append(doc_wrapper)          
        self.parent_node.notify_observers(
                app='Word',
                source='Application',
                event='NewDocument', 
                doc=doc)        
                
        
    def ApplicationEvents4_WindowDeactivate(self, this, doc, win):
        # When a window loses focus or it is destroyed, 
        # this will be triggered. 
        self.parent_node.notify_observers(
                app='Word',
                source='Application',
                event='WindowDeactivate', 
                doc=doc, win=win)
        
        
    def ApplicationEvents4_Quit(self, this):
        self.parent_node._on_app_quit(self)
        self.parent_node.notify_observers(
                app='Word',
                source='Application',
                event='Quit')
        
    def DocumentEvents2_Close(self, this, doc_wrapper):
        self.parent_node.notify_observers(
                app='Word',
                source='Document',
                event='Close')
        self._doc_list.remove(doc_wrapper)
            


class MSOffice(NodeDict, Observable):
    _prog_info = {
        'word':  {'id':'Word.Application', 'class':WordObject},
        'excel': {'id':'Excel.Application', 'class':ExcelObject}
    }
    
    def __init__(self, *args, **kwargs):
        NodeDict.__init__(self, *args, **kwargs)
        Observable.__init__(self)
        
        
    def _generate_object(self, app_name, func):
        app_name = app_name.lower()
        com_handle = func(self._prog_info[app_name]['id'])
        
        # Word Application does not have Hwnd property.
        if hasattr(com_handle, 'Hwnd'):
            for id_ in self:
                if hasattr(self[id_].com_handle, 'Hwnd') and self[id_].com_handle.Hwnd == com_handle.Hwnd:
                    return id_
        
        wrapper = self._prog_info[app_name]['class'](com_handle=com_handle)
        object_id = id(wrapper)
        self[object_id] = wrapper
        wrapper.show_window()
        
        if app_name == 'word':
            # The connection object should be stored, 
            # or it will be gabage collected, and consequently, 
            # event sink will not be notified any more. 
            connection = client.GetEvents(wrapper.com_handle, wrapper)
            wrapper._event_connection = connection
            # Set event handler for each document object.
            for idx in range(com_handle.Documents.Count):
                idx1 = idx + 1
                doc_wrapper = WordDocumentObject(
                        parent=wrapper, 
                        handle=com_handle.Documents.Item(idx1))
                doc_wrapper._event_connection = client.GetEvents(
                        doc_wrapper.com_handle, 
                        doc_wrapper)
                wrapper._doc_list.append(doc_wrapper)
                
        return object_id
        

    @WaveSynScriptAPI        
    def get_active(self, app_name):
        app_name = self.root_node.gui.dialogs.constant_handler_ASK_LIST_ITEM(
            app_name,
            the_list=['Word', 'Excel'],
            message='Which app you want to get?'
        )
        app_name = app_name.lower()
        return self._generate_object(app_name, client.GetActiveObject)
        
        
    @WaveSynScriptAPI
    def create(self, app_name):
        app_name = self.root_node.gui.dialogs.constant_handler_ASK_LIST_ITEM(
            app_name,
            the_list=['Word', 'Excel'],
            message='Which app you want to create?'
        )
        app_name = app_name.lower()
        return self._generate_object(app_name, client.CreateObject)
    
    
    @WaveSynScriptAPI
    def read_excel_clipboard(self, 
        map_func=None,
        strip_cells=False,
        return_dataframe=False,
        column_labels=None):
        try:
            table = self.root_node.lang_center.html_utils.get_tables(
                html_code=self.root_node.lang_center.wavesynscript.constants.CLIPBOARD_HTML,
                strip_cells=strip_cells)[0]
        except IndexError:
            raise ValueError("No table in clipboard.")
        if map_func:
            self.root_node.lang_center.python.table_utils.map(map_func, table)
        if return_dataframe:
            if not column_labels:
                column_labels = table[0]
                table = table[1:]
            import pandas
            table = pandas.DataFrame(table, columns=column_labels)
        return table
    
    
    def write_excel_clipboard(self, table):
        self.root_node.interfaces.os.clipboard.write(content=table, table=True)
        
    
    def _on_app_quit(self, app_obj):
        del self[id(app_obj)]
        

        