# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 01:09:40 2018

@author: Feng-cong Li
"""

from pathlib import Path

from . import BasePlugin



class Plugin(BasePlugin):
    _type = Path
    
        
    def action(self, data):
        if self.test_data(data):
            self.root_node.gui.console.show_tips([{'type':'file_list', 'content':(str(data),)}])
            