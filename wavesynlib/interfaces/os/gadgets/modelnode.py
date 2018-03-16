# -*- coding: utf-8 -*-
"""
Created on Fri Mar 16 18:25:53 2018

@author: Feng-cong Li
"""
from subprocess import Popen
import webbrowser

from wavesynlib.languagecenter.wavesynscript import ModelNode, Scripting
from wavesynlib.languagecenter.utils import get_caller_dir


gadget_paths = {
    'cmd': 'cmd',
    'powershell':'powershell'}



class Gadgets(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
    @Scripting.printable
    def launch(self, gadget, *args):
        if gadget in gadget_paths:
            gadget_path = gadget_paths[gadget]
        else:
            gadget_path = str(get_caller_dir() / gadget)
        
        if args:
            cmd = ['python', gadget_path]
            args = [str(arg) for arg in args]
            cmd.extend(args)
            Popen(cmd)
        else:
            webbrowser.open(gadget_path)