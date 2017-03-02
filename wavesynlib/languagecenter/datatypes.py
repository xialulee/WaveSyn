# -*- coding: utf-8 -*-
"""
Created on Sat Dec 26 21:10:54 2015

@author: Feng-cong Li
"""
from __future__  import print_function

import sys
import json
from six.moves import zip as izip
from collections import OrderedDict


class CommandSlot(object):
    __slots__ = [
        'source', # Where the command come from. For security considerations, e.g., if a command is received by xmlrpcserver, the source will be set to something indicating that the source may be malicious. {'native', 'local', 'remote'}
        'node_list', # The nodes comprise the path. For security considerations, e.g., we can forbid a node being obtained by commands from other machines.
        'method_name', # The name of the method being called.
        'args', # The arguments.
        'kwargs' # The keyword arguments.
    ]
    
    def __init__(self, source=None, node_list=None, 
                 method_name=None, args=None, kwargs=None):
        self.source = source
        self.node_list = node_list
        self.method_name = method_name
        self.args = args if args is not None else ()
        self.kwargs = kwargs if kwargs is not None else {}


class Table(object):
    def __init__(self, head):
        self.__head     = head
        self.__buf      = []
        
        
    @property
    def head(self):
        return self.__head
        
        
    @head.setter
    def head(self, value):
        self.__head = value
        
        
    def generate_row(self, row):
        d   = OrderedDict()
        for key, value in izip(self.__head, row):
            d[key]  = value
        return d
        
        
    def buffer_append(self, row):
        row         = self.generate_row(row)
        self.__buf.append(row)
        
        
    def __plain_row(self, row):
        return '\t'.join([str(v) for v in row.values()])
        
        
    def print_row(self, row, lang='json', target=sys.stdout):
        dump_func   = {'json':json.dumps, 'plain':self.__plain_row}
        row         = self.generate_row(row)
        rowString   = dump_func[lang](row)
        print(rowString, file=target)
        
        
    def print_buffer(self, lang='json', target=sys.stdout):
        dump_func    = {'json':json.dumps}
        tableStr    = dump_func[lang](self.__buf)
        print(tableStr, file=target)
        
        
    def print_head(self):
        print(*self.head, sep='\t')
        
        

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