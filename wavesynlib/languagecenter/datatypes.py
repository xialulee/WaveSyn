# -*- coding: utf-8 -*-
"""
Created on Sat Dec 26 21:10:54 2015

@author: Feng-cong Li
"""
from __future__  import print_function

import sys
import json
from itertools   import izip
from collections import OrderedDict

class Table(object):
    def __init__(self, head):
        self.__head     = head
        self.__buf      = []
        
    def __generateRow(self, row):
        d   = OrderedDict()
        for key, value in izip(self.__head, row):
            d[key]  = value
        return d
        
    def bufferAppend(self, row):
        row         = self.__generateRow(row)
        self.__buf.append(row)
        
    def printRow(self, row, lang='json', target=sys.stdout):
        dumpFunc    = {'json':json.dumps}
        row         = self.__generateRow(row)
        rowString   = dumpFunc[lang](row)
        print(rowString, file=target)
        
    def printBuffer(self, lang='json', target=sys.stdout):
        dumpFunc    = {'json':json.dumps}
        tableStr    = dumpFunc[lang](self.__buf)
        print(tableStr, file=target)
        
    


if __name__ == '__main__':
    lang    = sys.argv[1]
    if lang == '--outlang=json':
        lang    = 'json'
    row     = [int(v) for v in sys.argv[2:]]
    table   = Table(['C1', 'C2', 'C3', 'C4'])
    for k in range(16):
        table.printRow([k*v for v in row], lang=lang)
        
    # Powershell:
    # ./wavesynsource datatypes.py 1 2 3 4 | where {$_ -eq 5}