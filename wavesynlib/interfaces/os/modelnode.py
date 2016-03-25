# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 19:12:09 2016

@author: Feng-cong Li
"""

from __future__ import print_function, division, unicode_literals

import platform

from wavesynlib.languagecenter.wavesynscript import Scripting, ModelNode
from wavesynlib.languagecenter.utils import eval_format


class OperatingSystem(ModelNode):
    def _not_implemented(*args, **kwargs):
        raise NotImplementedError
    
    _sys_name = platform.system().lower()        
    _obj_map = {'winopen':'wavesynlib.interfaces.os.{_sys_name}.shell.winopen', 
                'get_memory_usage':'wavesynlib.interfaces.os.{_sys_name}.memstatus'}
    
    for name in _obj_map:
        try:
            __mod = __import__(eval_format(_obj_map[name]), globals(), locals(), [name], -1)
            _obj_map[name] = getattr(__mod, name)
        except ImportError:
            _obj_map[name] = _not_implemented
            
    
    def __init__(self, *args, **kwargs):
        ModelNode.__init__(self, *args, **kwargs)
    
    @Scripting.printable    
    def win_open(self, path):
        func = self._obj_map['winopen']
        return func(path)
        
    @Scripting.printable
    def get_memory_usage(self):
        func = self._obj_map['get_memory_usage']
        try:
            return func()
        except NotImplementedError:
            return 0