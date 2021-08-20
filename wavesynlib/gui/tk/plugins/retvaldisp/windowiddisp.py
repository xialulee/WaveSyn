# -*- coding: utf-8 -*-
"""
Created on Fri Mar  2 19:21:51 2018

@author: Feng-cong Li
"""

from wavesynlib.languagecenter.datatypes import TypeLinks

from . import BasePlugin


class Plugin(BasePlugin):
    _type = TypeLinks
    
        
    def action(self, data):
        if self.test_data(data):           
            info_list = data.get_link_info()
            links = []
            for info in info_list:
                links.append({'type':'link', 'content':info[0], 'command':info[1], 'end':' '})
            links.append({'type':'text', 'content':'\n'})             
            self.root_node.gui.console.show_tips(links)
