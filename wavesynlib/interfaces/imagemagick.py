# -*- coding: utf-8 -*-
"""
Created on Sun Apr 29 01:06:16 2018

@author: Feng-cong Li
"""

import sys
import io
import time
import json
from pathlib import Path
import subprocess as sp

from wavesynlib.languagecenter.wavesynscript import Scripting, ModelNode



class Command(ModelNode):
    def __init__(self, input_):
        super().__init__()
        if isinstance(input_, (str, Path)):
            self.__is_path = True
            self.__input = str(input_)
        else:
            self.__is_path = False
            self.__input = '-'
            self.__inobj = input_
        self.__args = ['magick', self.__input]
        
        
    def resize(self, 
               width:int=0, height:int=0, 
               width_percent:str='', height_percent:str='', 
               percent:int=0,
               keep_aspect_ratio=True,
               minval=False,
               shrink=False,
               enlarge=False):
        if width or height:
            arg = ''
            if width:
                arg = f'{width}'
            if height:
                arg = f'{arg}x{height}'
            if not keep_aspect_ratio:
                arg = f'{arg}!'
            if minval:
                arg = f'{arg}^'
            if shrink:
                arg = f'{arg}>'
            if enlarge:
                arg = f'{arg}<'
        elif width_percent and height_percent:
            arg = f'{width_percent}%x{height_percent}%'
        elif percent:
            arg = f'{percent}%'
        else:
            raise ValueError('Invalid arguments.')
        self.__args.extend(('-resize', arg))
        return self
    
    
    def crop(self, width:int, height:int, x:int=None, y:int=None):
        sign = lambda n: '-' if n<0 else '+'
        arg = f'{width}x{height}'
        if x is not None and y is not None:
            arg = f'{arg}{sign(x)}{abs(x)}{sign(y)}{abs(y)}'
        self.__args.extend(('-crop', arg))
        return self
    
    
    def set_colorspace(self, colorspace):
        self.__args.extend(('-colorspace', colorspace))
        return self
    
    
    def equalize(self):
        self.__args.append('-equalize')
        return self
        
        
    def save(self, output, format_='png', on_finish='notify'):
        if on_finish == 'notify':
            def on_finish(stdout, stderr, returncode, deltaT):
                if stderr:
                    print(stderr, file=sys.stderr)
                print(f'''ImageMagick task finished.
Task ID:\t\t{id(self)} 
Execution time:\t{deltaT}s.
Return code:\t\t{returncode}''')
        if isinstance(output, (str, Path)):
            self.__args.append(str(output))
        elif isinstance(output, io.IOBase):
            self.__args.append(f'{format_}:-')
        #print(self.__args)
        p = sp.Popen(self.__args, stderr=sp.PIPE)
        @self.root_node.thread_manager.new_thread_do
        def call_magick():
            start = time.time()
            retval = p.communicate()
            deltaT = time.time() - start
            @self.root_node.thread_manager.main_thread_do(block=False)
            def finish():
                on_finish(retval[0], retval[1], p.returncode, deltaT)
        return id(self)



class ImageMagickNode(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
    def open(self, image):
        cmd = Command(image)
        cmd.parent_node = self
        return cmd
    
    
    @Scripting.printable
    def get_info(self, path, *args):
        params = []
        for arg in args:
            if arg == 'size':
                params.append('"size":[%w,%h]')
            elif arg == 'depth':
                params.append('"depth":%z')
            elif arg == 'filesize':
                params.append('"filesize":"%b"')
        fstr = ','.join(params)
        fstr = '{'+fstr+'}'
        p = sp.Popen(['magick', 'identify', '-format', fstr, str(path)], 
                      stdout=sp.PIPE)
        retval = p.communicate()
        retval = retval[0].decode('ascii')
        retval = json.loads(retval)
        return retval
    
    
    @Scripting.printable
    def get_available_colorspaces(self):
        p = sp.Popen(['magick', '-list', 'colorspace'], stdout=sp.PIPE)
        retval = p.communicate()
        return retval[0].decode('ascii').split()
        