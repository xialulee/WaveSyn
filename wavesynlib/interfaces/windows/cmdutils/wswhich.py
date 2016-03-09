# -*- coding: utf-8 -*-
"""
Created on Fri Nov 06 09:30:21 2015

@author: Feng-cong Li
"""
from __future__ import print_function

import os
import sys
import getopt

from itertools import product
from collections import OrderedDict

from wavesynlib.interfaces.windows.shell.winopen import winopen

ERROR_NOERROR, ERROR_NOTFOUND, ERROR_PARAM = range(3)


def usage():
    pass # TODO


def main(argv):
    try:
        opts, args = getopt.getopt(argv[1:], \
            'a',\
            ['all', 'winopen']\
        ) # TODO
    except getopt.GetoptError, err:
        print(str(err), file=sys.stderr)
        usage()
        return ERROR_PARAM
        
    all_cmd  = False
    wopen   = False
    for o, a in opts:
        if o in ('-a', '--all'):
            all_cmd = True
        if o == '--winopen':
            wopen   = True
    
    name        = args[0]
    name, ext   = os.path.splitext(name)
    paths       = os.environ['PATH'].split(os.path.pathsep)
    exts        = os.environ['PATHEXT'].split(os.path.pathsep)
    
    if ext: 
        if ext.upper() not in [e.upper() for e in exts]:
            print('The file {} is not executable.'.format(args[0]), file=sys.stderr)        
            return ERROR_NOTFOUND
        else:
            exts = [ext]

    paths.insert(0, '.')
    
    file_paths = OrderedDict()
        
    for path, ext in product(paths, exts):
        testPath = ''.join([os.path.join(path, name), ext])
        if os.path.exists(testPath):
            abs_test_path    = os.path.abspath(testPath)
            #if abs_test_path not in file_paths: 
            # Prevent redundant output
            abs_test_path = os.path.normcase(abs_test_path) 
            file_paths[abs_test_path] = True
            if not all_cmd:
                break        
            
    if file_paths:
        for file_path in file_paths:
            print(file_path)
            if wopen:
                winopen(file_path)
    else:
        print('wswhich.py: no {} in ({})'.format(name, os.path.pathsep.join(paths)), file=sys.stderr)
        return ERROR_NOTFOUND
    return ERROR_NOERROR
    
    
    
if __name__ == '__main__':
    sys.exit(main(sys.argv))
    