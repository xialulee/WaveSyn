# -*- coding: utf-8 -*-
"""
Created on Wed Jan 23 19:32:21 2019

@author: Feng-cong Li
"""

from wavesynlib.languagecenter.hyhdl.hyhdl2myhdl import main as hyhdl_to_myhdl
import importlib
import os.path
import sys



importlib.machinery.SOURCE_SUFFIXES.insert(0, '.hyhdl')
_original_source_to_code = importlib.machinery.SourceFileLoader.source_to_code


def _hyhdl_source_to_code(self, data, path, _optimize=-1):
    p, ext = os.path.splitext(path)
    new_path = p + '.py'    
    if ext == '.hyhdl':
        if not os.path.exists(new_path) or \
                os.path.getmtime(path) > os.path.getmtime(new_path):
            hyhdl_to_myhdl((None, path, new_path))
    with open(new_path, 'rb') as f:
        data = f.read()
    return _original_source_to_code(self, data, new_path, _optimize=_optimize)
        

importlib.machinery.SourceFileLoader.source_to_code = _hyhdl_source_to_code
sys.path_importer_cache.clear()
importlib.invalidate_caches()
