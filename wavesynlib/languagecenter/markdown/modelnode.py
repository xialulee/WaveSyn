# -*- coding: utf-8 -*-
"""
Created on Sun Mar 05 20:20:24 2017

@author: Feng-cong Li
"""

from __future__ import print_function, division, unicode_literals

from wavesynlib.languagecenter.wavesynscript import Scripting, ModelNode
from wavesynlib.languagecenter.markdown import utils


class Utils(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
    @Scripting.printable
    def generate_table(self, table):
        if hasattr(self.root_node.interfaces.os.clipboard, 'support_clipboard_html'):
            if table is self.root_node.lang_center.wavesynscript.constants.CLIPBOARD_HTML:                
                tables = self.root_node.lang_center.html_utils.get_tables(table)
                ret = []
                for table in tables:
                    ret.append(utils.generate_table(table))
                return '\n\n'.join(ret)
            else:
                return utils.generate_table(table)
        else:
            return utils.generate_table(table)