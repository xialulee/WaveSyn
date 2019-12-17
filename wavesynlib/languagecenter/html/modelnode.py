# -*- coding: utf-8 -*-
"""
Created on Sun Mar 05 17:50:52 2017

@author: Feng-cong Li
"""
import os
from pathlib import Path

from wavesynlib.languagecenter.wavesynscript import Scripting, ModelNode

# The following code generates the bytecode file of the 
# utils.hy which is written in Hy.
# If we import a module written in hy directly in wavesyn,
# it will fail, and I cannot figure out why. 
import hy
try:
    from wavesynlib.languagecenter.html import utils
except hy.errors.HyCompileError:
# After the bytecode file generated, we can import the module written by hy.    
    utils_path = Path(__file__).parent / 'utils.hy'
    os.system(f'hyc {utils_path}')
    from wavesynlib.languagecenter.html import utils
    


class Utils(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
    def _get_html_code(self, html_code=None, stream=None, file_path=None, encoding=None):
        if hasattr(self.root_node.interfaces.os.clipboard, 'constant_handler_CLIPBOARD_HTML'):
            html_code = self.root_node.interfaces.os.clipboard.constant_handler_CLIPBOARD_HTML(html_code)
        if html_code:
            pass
        elif stream:
            html_code = stream.read()
        elif file_path:
            kwargs = {}
            if encoding:
                kwargs['encoding'] = encoding
            with open(file_path, 'r', **kwargs) as f:
                html_code = f.read()
        else:
            pass # Raise some exception.
        return html_code
    
        
    @Scripting.wavesynscript_api
    def get_tables(self, html_code=None, stream=None, file_path=None, encoding=None, strip_cells=False):
        '''\
Translate <table>s in HTML code into Python nested lists.
On Windows platform, it can also retrive tables in clipboard, since MSOffice
put tables in clipboard using CF_HTML format.

html_code: the HTML code as a string (support CLIPBOARD_HTML const if the
        clipboard of the OS has the HTML mode).
    Default: None.
stream: if html_code is None and stream provided, the HTML code will be 
        obtained from this stream.
    Default: None.
file_path: if html_code and stream are None and file_path provided,
    the HTML code will be obtained by reading the provided file.
    Default: None.
encoding: the encoding of the HTML code. '''
        html_code = self._get_html_code(html_code, stream, file_path, encoding)
        return utils.get_table_text(html_code, strip=strip_cells)  
    
    
    @Scripting.wavesynscript_api
    def iterable_to_table(self, iterable, have_head=False):
        return utils.iterable_to_table(iterable, have_head)
