# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 22:34:54 2016

@author: Feng-cong Li
"""
import xml
import html
from html import parser



# See http://stackoverflow.com/a/9662410
remove_tags = lambda html_code: ''.join(xml.etree.ElementTree.fromstring(html_code).itertext())


class _TableTextExtractor(parser.HTMLParser, object):
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
    


def iterable_to_table(iterable, have_head=False):
    row_str = []
    for idx, row in enumerate(iterable):
        if idx==0 and have_head:
            start = '<th>'; stop = '</th>'
        else:
            start = '<td>'; stop = '</td>'
        items = []
        for item in row:
            item_str = html.escape(str(item))
            items.append(f'{start}{item_str}{stop}')
        a_row = ' '.join(items)
        row_str.append(f'<tr>{a_row}</tr>')
    table_str = '\n'.join(row_str)
    return f'''<table>
{table_str}
</table>'''
