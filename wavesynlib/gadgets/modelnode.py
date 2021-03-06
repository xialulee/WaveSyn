# -*- coding: utf-8 -*-
"""
Created on Fri Mar 16 18:25:53 2018

@author: Feng-cong Li
"""
import pathlib
from subprocess import Popen
import webbrowser
import tempfile

from wavesynlib.languagecenter.wavesynscript import ModelNode, Scripting, WaveSynScriptAPI


gadget_paths = {
    'cmd': 'cmd',
    'powershell':'powershell'}



class Gadgets(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
    @WaveSynScriptAPI
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
        if isinstance(image, (str, pathlib.Path)):
            args = [image]
        else:
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tfile:
                image.save(tfile, 'png')
            args = [tfile.name, '--delete']
        self.launch('wsdisplay.py', *args)        