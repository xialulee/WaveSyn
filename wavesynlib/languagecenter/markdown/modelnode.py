# -*- coding: utf-8 -*-
"""
Created on Sun Mar 05 20:20:24 2017

@author: Feng-cong Li
"""
import os
from pathlib import Path

# The following code generates the bytecode file of the 
# utils.hy which is written in Hy.
# If we import a module written in hy directly in wavesyn,
# it will fail, and I cannot figure out why. 
import hy
try:
    from wavesynlib.languagecenter.markdown import utils 
except hy.errors.HyCompileError:
# After the bytecode file generated, we can import the module written by hy.    
    utils_path = Path(__file__).parent / 'utils.hy'
    os.system(f'hyc {utils_path}')
    from wavesynlib.languagecenter.markdown import utils

from wavesynlib.languagecenter.wavesynscript import Scripting, ModelNode



class Utils(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
    @Scripting.printable
    def generate_table(self, table, head=None):
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

