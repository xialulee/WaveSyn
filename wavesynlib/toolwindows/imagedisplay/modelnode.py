# -*- coding: utf-8 -*-
"""
Created on Sun Jan 29 21:26:31 2017

@author: Feng-cong Li
"""
import _thread as thread
import tempfile
from subprocess import Popen
import numpy as np

from wavesynlib.languagecenter.wavesynscript import ModelNode, Scripting
from wavesynlib.languagecenter.utils import get_caller_dir


class DisplayLauncher(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    
    @Scripting.printable
    def launch(self, image):
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tfile:
            image.save(tfile, 'png')
        
        display_path = str(get_caller_dir() / 'display.py')
        Popen(['python', display_path, tfile.name])