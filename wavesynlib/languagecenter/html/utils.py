# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 22:34:54 2016

@author: Feng-cong Li
"""
from __future__ import annotations

from typing import Any, Iterable, List, Mapping
from html import parser, escape

from defusedxml import ElementTree
import pandas as pd



# See http://stackoverflow.com/a/9662410
def remove_tags(html_code: str) -> str:
    return ''.join(ElementTree.fromstring(html_code).itertext())



class Table:
    def __init__(self):
        self.has_head: bool = False
        self.rows: List[List[str]] = []
        

    def __getitem__(self, index: int) -> List[str]:
        return self.rows[index]
    

    @property
    def head(self) -> List[str] | None:
        if self.has_head:
            return self.rows[0]
        return None
    

    @property
    def body(self) -> List[List[str]]: 
        if self.has_head:
            return self.rows[1:]
        return self.rows
        

    def new_row(self) -> List[str]:
        row = []
        self.rows.append(row)
        return row
    

    def to_dataframe(self) -> pd.DataFrame:
        kwargs: Mapping[str, Any] = {
            "dtype": pd.StringDtype()
        }
        if self.has_head: 
            kwargs["columns"] = self.rows[0]
            self.rows = self.rows[1:]
        return pd.DataFrame(self.rows, **kwargs)



class TableTextExtractor(parser.HTMLParser):
    def __init__(self, tables: List) -> None:
        super().__init__()
        self.__tables = tables
        self.__current_table = None
        self.__current_row = None
        self.__in_td_tag = False

        
    def handle_starttag(self, tag, attrs):         
        # Todo: support tfoot
        if tag == "table":
            table = Table()
            self.__current_table = table
            self.__tables.append(table)
        elif tag == "tr":
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
            


def get_table_text(
        html_code: str, 
        strip: bool = False
    ) -> List[Table]:
    # Todo: implement strip
    retval = []
    extractor = TableTextExtractor(retval)
    extractor.feed(html_code)
    return retval
    


def iterable_to_table(
        iterable: Iterable, 
        has_head: bool = False
    ) -> str:
    row_str = []
    for idx, row in enumerate(iterable):
        if idx==0 and has_head:
            start = "<th>"; stop = "</th>"
        else:
            start = "<td>"; stop = "</td>"
        items = []
        for item in row:
            item_str = escape(str(item))
            items.append(f"{start}{item_str}{stop}")
        a_row = " ".join(items)
        row_str.append(f"<tr>{a_row}</tr>")
    table_str = "\n".join(row_str)
    return f"""\
<table>
{table_str}
</table>"""
