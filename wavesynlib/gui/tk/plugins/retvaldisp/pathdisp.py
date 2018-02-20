# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 01:09:40 2018

@author: Feng-cong Li
"""

from pathlib import Path



class Plugin:
    _type = Path
    
    def __init__(self, root_node):
        self.__root = root_node
        
        
    def test_data(self, data):
        if isinstance(data, self._type):
            return True
        else:
            return False
        
        
    def action(self, data):
        if self.test_data(data):
            self.__root.gui.console.show_tips([{'type':'file_list', 'content':(str(data),)}])
            