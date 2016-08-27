# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 22:34:54 2016

@author: Feng-cong Li
"""
from __future__ import print_function, division, unicode_literals

import xml
from six.moves import html_parser
from wavesynlib.languagecenter.wavesynscript import Scripting, ModelNode


# See http://stackoverflow.com/a/9662410
remove_tags = lambda html_code: ''.join(xml.etree.ElementTree.fromstring(html_code).itertext())


class _TableTextExtractor(html_parser.HTMLParser, object):
    def __init__(self, tables):
        super(_TableTextExtractor, self).__init__()
        self.__tables = tables
        self.__current_table = None
        self.__current_row = None
        self.__in_td_tag = False
        
    def handle_starttag(self, tag, attrs):         
        if tag == u'table':
            table = []
            self.__current_table = table
            self.__tables.append(table)
        elif tag == u'tr':
            row = []
            self.__current_table.append(row)
            self.__current_row = row
        elif tag == u'td':
            self.__in_td_tag = True
            self.__current_row.append('')
        elif tag == u'p' and self.__in_td_tag:
            cell = self.__current_row[-1]
            if cell:
                self.__current_row[-1] = cell + u'\n'
        
    def handle_endtag(self, tag):
        if tag == u'td':
            self.__in_td_tag = False
        
    def handle_data(self, data):
        if self.__in_td_tag:
            self.__current_row[-1] += data


def get_table_text(html_code):
    retval = []
    extractor = _TableTextExtractor(retval)
    extractor.feed(html_code)
    return retval
    

class HTMLUtils(ModelNode):
    def __init__(self, *args, **kwargs):
        super(HTMLUtils, self).__init__(*args, **kwargs)
        
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
        return get_table_text(html_code)    
    