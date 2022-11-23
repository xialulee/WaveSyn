# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 22:34:54 2016

@author: Feng-cong Li
"""
from __future__ import annotations

from typing import List
from dataclasses import dataclass
import html
from html import parser

from defusedxml import ElementTree
import pandas as pd



# See http://stackoverflow.com/a/9662410
def remove_tags(html_code: str) -> str:
    return ''.join(ElementTree.fromstring(html_code).itertext())



class Table:
    def __init__(self):
        self.has_head: bool = False
        self.rows: List[List[str]] = []
        

    def new_row(self) -> List[str]:
        row = []
        self.rows.append(row)
        return row
    

    def to_dataframe(self):
        kwargs = {"dtype": pd.StringDtype()}
        if self.has_head: 
            kwargs["columns"] = self.rows[0]
            self.rows = self.rows[1:]
        return pd.DataFrame(self.rows, **kwargs)



class TableTextExtractor(parser.HTMLParser):
    def __init__(self, tables):
        super().__init__()
        self.__tables = tables
        self.__current_table = None
        self.__current_row = None
        self.__in_td_tag = False

        
    def handle_starttag(self, tag, attrs):         
        if tag == "table":
            table = Table()
            self.__current_table = table
            self.__tables.append(table)
        elif tag == "tr":
#            row = []
#            self.__current_table.rows.append(row)
#            self.__current_row = row
            self.__current_row = self.__current_table.new_row()
        elif tag in ("td", "th"):
            self.__in_td_tag = True
            self.__current_row.append("")
            if not self.__current_table.has_head and tag == "th":
                self.__current_table.has_head = True
        elif tag == "p" and self.__in_td_tag:
            cell = self.__current_row[-1]
            if cell:
                self.__current_row[-1] = cell + "\n"

        
    def handle_endtag(self, tag):
        if tag in ("td", "th"):
            self.__in_td_tag = False

        
    def handle_data(self, data):
        if self.__in_td_tag:
            self.__current_row[-1] += data
            


def get_table_text(html_code, strip=False):
    retval = []
    extractor = TableTextExtractor(retval)
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
