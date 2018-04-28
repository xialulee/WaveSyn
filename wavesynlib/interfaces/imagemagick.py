# -*- coding: utf-8 -*-
"""
Created on Sun Apr 29 01:06:16 2018

@author: Feng-cong Li
"""

import io
from pathlib import Path
import subprocess as sp

from wavesynlib.languagecenter.wavesynscript import Scripting, ModelNode



class Command:
    def __init__(self, input_):
        if isinstance(input_, (str, Path)):
            self.__is_path = True
            self.__input = str(input_)
        else:
            self.__is_path = False
            self.__input = '-'
        self.__args = ['magick', self.__input]
        
        
    def resize(self, width, height):
        self.__args.extend(('-resize', f'{width}x{height}'))
        return self
    
    
    def crop(self, x, y, width, height):
        self.__args.extend(('-crop', f'{width}x{height}+{x}+{y}'))
        return self
        
        
    def save(self, output, format_='png'):
        if isinstance(output, (str, Path)):
            self.__args.append(str(output))
        elif isinstance(output, io.IOBase):
            self.__args.append(f'{format_}:-')
        #print(self.__args)
        p = sp.Popen(self.__args)
        p.communicate()



class ImageMagickNode(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
    def open(self, image):
        return Command(image)