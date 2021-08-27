# -*- coding: utf-8 -*-
"""
Created on Fri Apr 07 17:08:49 2017

@author: Feng-cong Li
"""

import abc



class BasePlugin(abc.ABC):
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


    @abc.abstractmethod
    def action(self, data):
        pass
