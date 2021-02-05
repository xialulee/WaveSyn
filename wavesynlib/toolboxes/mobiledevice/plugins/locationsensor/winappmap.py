# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 23:46:27 2017

@author: Feng-cong Li
"""

# The class whose instance handles certain type of data,
# should be named as "Plugin".
class Plugin:
    link_text = 'Windows Map App'
    support_os = 'Windows'
    
    
    def __init__(self, root_node):
        '''root_node: the root node of WaveSyn.'''
        self.__root = root_node
    
    
    def test_data(self, data):
        '''The link of the plugin action will be displayed 
if this method returns True'''
        return True # Always handles the location data.
    
    
    def action(self, data):
        '''This is the procedure being executed while its link being clicked.'''
        with self.__root.code_printer():
            self.__root.interfaces.os.map_open(
                latitude=data['latitude'], 
                longitude=data['longitude'])
        