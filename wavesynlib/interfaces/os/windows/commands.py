# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 23:05:32 2018

@author: Feng-cong Li
"""

import sys
import locale
from subprocess import run, PIPE

from wavesynlib.languagecenter.wavesynscript import ModelNode



class Route(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
    def add(self, 
            destination, mask, gateway, 
            metric=None, interface=None, 
            persistent=False):
        args = ['route']
        if persistent:
            args.append('-p')
        args.extend(['add', destination, 'mask', mask, gateway])
        if metric:
            args.extend(['metric', str(metric)])
        if interface:
            args.extend(['if', interface])
            
        ret = run(args, stdout=PIPE, stderr=PIPE)
        
        if ret.stderr:
            print(ret.stderr.decode(locale.getpreferredencoding()), file=sys.stderr)
        if ret.stdout:
            print(ret.stdout.decode(locale.getpreferredencoding()), file=sys.stdout)
            
        return ret.returncode
        


class Commands(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.route = ModelNode(
            is_lazy=True,
            class_object=Route)
        
        
    