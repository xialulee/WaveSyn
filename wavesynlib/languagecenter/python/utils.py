# -*- coding: utf-8 -*-
"""
Created on Sat Feb  3 00:51:32 2018

@author: Feng-cong Li
"""
from copy import deepcopy

from wavesynlib.languagecenter.wavesynscript import ModelNode, Scripting, WaveSynScriptAPI



class TableUtils(ModelNode):
    '''Utils for operating tables.
Table in this context means matrix (with row and column) implemented by nested lists.
The utils provided by this node can be used to operate tables on web pages,
MSWord, MS Excel, and so on.'''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
    @WaveSynScriptAPI
    def transpose(self, table):
        '''Transpose a table.
Only applicable for rectangular tables.'''
        height = len(table)
        width = len(table[0])
        ret = []
        for c in range(width):
            row = []
            for r in range(height):
                row.append(table[r][c])
            ret.append(row)
        return ret
    
    
    @WaveSynScriptAPI
    def map(self, func, table, inplace=True):
        if not inplace:
            table = deepcopy(table)
        for row in table:
            for idx, item in enumerate(row):
                row[idx] = func(item)
        if not inplace:
            return table
        
        
    @WaveSynScriptAPI
    def from_2darray(self, array):
        '''Convert 2-D NumPy array to table, i.e., nested python lists.'''
        ret = list(array)
        return [list(item) for item in ret]
    
    
    @WaveSynScriptAPI
    def flatten(self, table):
        ret = table[0]
        for row in table[1:]:
            ret.extend(row)
        return ret
    