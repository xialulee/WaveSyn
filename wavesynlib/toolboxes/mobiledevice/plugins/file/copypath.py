# -*- coding: utf-8 -*-
"""
Created on Sat Sep 23 11:45:16 2017

@author: Feng-cong Li
"""

class Plugin:
    link_text = 'Copy Path'
    support_os = 'all'
    
    
    def __init__(self, root_node):
        self.__root = root_node
        
        
    def test_data(self, data):
        return True
    
    
    def action(self, data):
        with self.__root.code_printer():
            self.__root.interfaces.os.clipboard.write(data)
