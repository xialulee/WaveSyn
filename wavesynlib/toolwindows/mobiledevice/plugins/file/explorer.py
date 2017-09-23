# -*- coding: utf-8 -*-
"""
Created on Sun Sep 24 00:28:57 2017

@author: Feng-cong Li
"""

class Plugin:
    link_text = 'Explore'
    support_os = 'all'
    
    
    def __init__(self, root_node):
        self.__root = root_node
        
        
    def test_data(self, data):
        return True
    
    
    def action(self, data):
        with self.__root.code_printer():
            self.__root.interfaces.os.win_open(data)
