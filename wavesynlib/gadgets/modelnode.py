# -*- coding: utf-8 -*-
"""
Created on Fri Mar 16 18:25:53 2018

@author: Feng-cong Li
"""
import pathlib
from subprocess import Popen
import webbrowser
import tempfile

from wavesynlib.languagecenter.wavesynscript import ModelNode, Scripting


gadget_paths = {
    'cmd': 'cmd',
    'powershell':'powershell'}



class Gadgets(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
    @Scripting.wavesynscript_api
    def launch(self, gadget, *args):
        if gadget in gadget_paths:
            gadget_path = gadget_paths[gadget]
        else:
            gadget_path = str(pathlib.Path(__file__).parent / gadget)
        
        if args:
            cmd = ['python', gadget_path]
            args = [str(arg) for arg in args]
            cmd.extend(args)
            Popen(cmd)
        else:
            webbrowser.open(gadget_path)
            
            
    def display_image(self, image):
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tfile:
            image.save(tfile, 'png')
        self.launch('wsdisplay.py', tfile.name, '--delete')        