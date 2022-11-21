# -*- coding: utf-8 -*-
"""
Created on Sun Mar 05 20:20:24 2017

@author: Feng-cong Li
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import List

from wavesynlib.languagecenter.wavesynscript import Scripting, WaveSynScriptAPI, ModelNode
from . import utils



class Utils(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
    @WaveSynScriptAPI
    def generate_table(self, 
            table: List[List], 
            head: List|None = None
        ) -> str:
        if hasattr(self.root_node.interfaces.os.clipboard, 'constant_handler_CLIPBOARD_HTML'):
            if table is self.root_node.lang_center.wavesynscript.constants.CLIPBOARD_HTML:                
                tables = self.root_node.lang_center.html_utils.get_tables(table)
                ret = []
                for table in tables:
                    ret.append(utils.table_to_code(table, head))
                return '\n\n'.join(ret)
            else:
                return utils.table_to_code(table, head)
        else:
            return utils.table_to_code(table, head)

