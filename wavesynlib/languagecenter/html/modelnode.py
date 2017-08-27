# -*- coding: utf-8 -*-
"""
Created on Sun Mar 05 17:50:52 2017

@author: Feng-cong Li
"""
from __future__ import print_function, division, unicode_literals

from wavesynlib.languagecenter.wavesynscript import Scripting, ModelNode
from wavesynlib.languagecenter.html import utils


class Utils(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def _get_html_code(self, html_code=None, stream=None, file_path=None, encoding=None):
        if hasattr(self.root_node.interfaces.os.clipboard, 'support_clipboard_html'):
            html_code = self.root_node.interfaces.os.clipboard.support_clipboard_html(html_code)
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
        
    @Scripting.printable
    def get_tables(self, html_code=None, stream=None, file_path=None, encoding=None):
        '''Translate <table>s in HTML code into Python nested lists.
On Windows platform, it can also retrive tables in clipboard, since MSOffice
put tables in clipboard using CF_HTML format.'''
        html_code = self._get_html_code(html_code, stream, file_path, encoding)
        return utils.get_table_text(html_code)  