# -*- coding: utf-8 -*-
"""
Created on Tue Aug  7 02:17:32 2018

@author: Feng-cong Li
"""

import platform
from wavesynlib.languagecenter.wavesynscript import ModelNode



class DNS(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def edit_hosts(self, editor=None):
        system = platform.system()
        if system == "Windows":
            self.root_node.interfaces.os.windows.edit_hosts(editor=editor)
        else:
            raise NotImplementedError("Not implemented on this platform.")


    def get_hosts_path(self):
        system = platform.system()
        if system == "Windows":
            return self.root_node.interfaces.os.windows.get_hosts_path()
        else:
            raise NotImplementedError("Not implemented on this platform.")



class Net(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.apnic = ModelNode(
            is_lazy = True,
            module_name='wavesynlib.interfaces.net.apnic.modelnode',
            class_name='APNIC')

        self.dns = ModelNode(
            is_lazy=True,
            class_object=DNS)
