# -*- coding: utf-8 -*-
"""
Created on Thu Mar 02 22:41:20 2017

@author: Feng-cong Li
"""

from __future__ import print_function, division, unicode_literals

import os
from subprocess import Popen

from wavesynlib.languagecenter.utils import get_caller_dir
from wavesynlib.languagecenter.wavesynscript import Scripting, ModelNode
from wavesynlib.interfaces.os.windows.wmi import WQL


app_paths = {
    'cmd': 'cmd'
}


class WMI(ModelNode):
    def __init__(self, *args, **kwargs):
        super(WMI, self).__init__(*args, **kwargs)
        self.__wql = None
       
    @Scripting.printable
    def query(self, wql, output_format='original'):
        if self.__wql is None:
            # Lazy init.
            self.__wql = WQL()
        return self.__wql.query(wql, output_format)


class Windows(ModelNode):
    def __init__(self, *args, **kwargs):
        super(Windows, self).__init__(*args, **kwargs)
        self.wmi = WMI()
        
    
    @Scripting.printable
    def launch(self, app_name, *args):
        if app_name in app_paths:
            app_path = app_paths[app_name]
        else:
            self_dir = get_caller_dir()
            app_path = os.path.join(self_dir, 'apps', app_name)
        
        cmd = ['python', app_path]
        if args:
            args = [str(arg) for arg in args]
        cmd.extend(args)
        Popen(cmd)
        
        