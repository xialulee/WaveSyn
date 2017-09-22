# -*- coding: utf-8 -*-
"""
Created on Fri Sep 22 12:07:16 2017

@author: Feng-cong Li
"""
import json



class Plugin:
    link_text = 'Copy JSON'
    support_os = 'all'
    
    
    def __init__(self, root_node):
        self.__root = root_node
        
        
    def test_data(self, data):
        return True
    
    
    def action(self, data):
        s = json.dumps(data)
        with self.__root.code_printer():
            self.__root.interfaces.os.clipboard.write(s)
