# -*- coding: utf-8 -*-
"""
Created on Sat Mar 04 21:02:17 2017

@author: Feng-cong Li
"""

from __future__ import division, print_function, unicode_literals

from comtypes import client
import json



class WQL(object):
    def __init__(self):
        loc = client.CreateObject('WbemScripting.SWbemLocator')
        self.__server = loc.ConnectServer('.')
        
        
    def query(self, wql_str, output_format='original'):
        items = self.__server.ExecQuery(wql_str)

        def to_native(items):
            result = []
            for item in items:
                d = {}
                for prop in item.Properties_:
                    d[prop.Name] = prop.Value
                result.append(d)
            return result
            
        def to_json(items):
            result = to_native(items)
            return json.dumps(result)
        
        def identity(items):
            return items
        
        return {
            'original': identity,
            'comtypes': identity,
            'native': to_native,
            'python': to_native,
            'json': to_json
        }[output_format](items)