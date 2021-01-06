# -*- coding: utf-8 -*-
"""
Created on Sat Dec 26 21:10:54 2015

@author: Feng-cong Li
"""
import sys
import json
from collections import OrderedDict
from abc import ABC, abstractmethod
from dataclasses import dataclass



import os
from pathlib import Path
from typing import Callable
import hy
try:
    from wavesynlib.languagecenter.datatypes import treetype
except hy.errors.HyCompilerError:
    hy_path = Path(__file__).parent / 'treetype.hy'
    os.system(f'hyc {hy_path}')
    from wavesynlib.languagecenter.datatypes import treetype

from wavesynlib.languagecenter.designpatterns import Observable



class ArgType:
    pass


class ArgOpenFile(ArgType):
    pass


class ArgSaveAs(ArgType):
    pass


class ArgChooseDir(ArgType):
    pass



@dataclass
class Event:
    sender: object
    name: str = ""



class CommandObject(Observable):
    def __init__(self, execute: Callable, can_execute: Callable = None):
        self.__execute = execute
        self.__can_execute = can_execute
        super().__init__()


    def can_execute(self):
        retval = None
        if self.__can_execute is None:
            retval = True
        else:
            retval = self.__can_execute()
        return retval
        

    def change_can_execute(self):
        self.notify_observers(Event(sender=self, name="can_execute_changed"))


    def __call__(self):
        retval = None
        if self.can_execute():
            retval = self.__execute()
        else:
            retval = None
        return retval



class CommandSlot:
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



class Table:
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
        for key, value in zip(self.__head, row):
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



class LookupTable:
    def __init__(self, data, key_index, value_index):
        self.__data = data
        self.__key_index = key_index
        self.__value_index = value_index


    def lookup(self, key):
        for row in self.__data:
            if row[self.__key_index] == key:
                return row[self.__value_index]
        
        
        
class TypeLinks(ABC):
    @abstractmethod
    def get_link_info(self): pass
        
        

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