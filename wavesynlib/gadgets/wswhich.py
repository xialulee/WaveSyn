#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 06 09:30:21 2015

@author: Feng-cong Li
"""

import os
import sys
import getopt
import pathlib
import platform

from itertools import product
from collections import OrderedDict

from wavesynlib.interfaces.os.windows.shell.winopen import winopen
from wavesynlib.languagecenter.datatypes import Table

ERROR_NOERROR, ERROR_NOTFOUND, ERROR_PARAM = range(3)


def usage():
    pass # TODO
    
    

def which(name, all_=False, cwd=False):
    p = pathlib.Path(name)
    suffixes = p.suffixes
    ext = suffixes[-1] if suffixes else ''
    paths = os.environ['PATH'].split(os.path.pathsep)
    if platform.system() == 'Windows':
        exts = os.environ['PATHEXT'].split(os.path.pathsep)
        if ext:
            if ext.upper() not in [e.upper() for e in exts]:
                raise TypeError(f'The file {name} is not executable.')
            else:
                exts = [ext]
    else:
        if ext:
            exts = [ext]
        else:
            exts = ['']
    if cwd:
        paths.insert(0, '.')
    
    file_paths = OrderedDict()    
    
    for path, ext in product(paths, exts):
        path = pathlib.Path(path)
        test_path = path / f'{str(name)}{ext}'
        if test_path.exists():
            abs_test_path = test_path.absolute()
            file_paths[abs_test_path] = True
            if not all_:
                break        
    
    return tuple(file_paths)
    


def main(argv):
    try:
        opts, args = getopt.getopt(argv[1:], \
            'a',\
            ['all', 'winopen', 'jsontable', 'cwd', 'order=']\
        ) # TODO
    except getopt.GetoptError as err:
        print(str(err), file=sys.stderr)
        usage()
        return ERROR_PARAM
        
    all_cmd = False
    wopen = False
    json_output = False
    cmd_order = -1
    cwdfirst = False
    for o, a in opts:
        if o in ('-a', '--all'):
            all_cmd = True
        if o == '--winopen':
            wopen   = True
        if o == '--jsontable':
            json_output = True
        if o == '--cwd':
            cwdfirst = True
        if o == '--order':
            cmd_order = int(a)
            all_cmd = True
    
    name = args[0]
    try:
        file_paths = which(name, all_=all_cmd, cwd=cwdfirst)
    except TypeError as err:
        print('The file {} is not executable.'.format(args[0]), file=sys.stderr) 
        return ERROR_NOTFOUND
            
    if file_paths:
        table = Table(['order', 'path'])
        for order, file_path in enumerate(file_paths):
            if (cmd_order<0) or (cmd_order==order):
                if not json_output:
                    print(file_path)
                else:
                    table.print_row((order, str(file_path)))
                if wopen:
                    winopen(file_path)
    else:
        print(f'wswhich.py: no {name} in ({os.environ["PATH"]})', 
              file=sys.stderr)
        return ERROR_NOTFOUND
    return ERROR_NOERROR
    
    
    
if __name__ == '__main__':
    sys.exit(main(sys.argv))
    
