# -*- coding: utf-8 -*-
"""
Created on Thu Mar 02 22:41:20 2017

@author: Feng-cong Li
"""

from __future__ import print_function, division, unicode_literals

import os
import webbrowser

from wavesynlib.languagecenter.utils import get_caller_dir
from wavesynlib.languagecenter.wavesynscript import Scripting, ModelNode


app_paths = {
    'cmd': 'cmd'
}


class Windows(ModelNode):
    def __init__(self, *args, **kwargs):
        super(Windows, self).__init__(*args, **kwargs)
        
    
    @Scripting.printable
    def launch(self, app_name):
        if app_name in app_paths:
            app_path = app_paths[app_name]
        else:
            self_dir = get_caller_dir()
            app_path = os.path.join(self_dir, 'apps', app_name)
        webbrowser.open(app_path)