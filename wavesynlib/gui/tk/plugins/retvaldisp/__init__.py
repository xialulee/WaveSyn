# -*- coding: utf-8 -*-
"""
Created on Fri Apr 07 17:08:49 2017

@author: Feng-cong Li
"""

class BasePlugin:
    _type = None

    def __init__(self, root_node):
        self.__root = root_node


    @property
    def root_node(self):
        return self.__root


    def test_data(self, data):
        if isinstance(data, self._type):
            return True
        else:
            return False
