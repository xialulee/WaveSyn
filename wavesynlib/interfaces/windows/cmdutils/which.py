# -*- coding: utf-8 -*-
"""
Created on Fri Nov 06 09:30:21 2015

@author: Feng-cong Li
"""
from __future__ import print_function

import os
import getopt
import sys

from itertools import product

ERROR_NOERROR, ERROR_NOTFOUND, ERROR_PARAM = range(3)


def usage():
    pass # TODO


def main(argv):
    try:
        opts, args = getopt.getopt(argv[1:], \
            '',\
            []\
        ) # TODO
    except getopt.GetoptError, err:
        print(str(err), file=sys.stderr)
        usage()
        return ERROR_PARAM
    
    name    = args[0]
    paths   = os.environ['PATH'].split(os.path.pathsep)
    exts    = os.environ['PATHEXT'].split(os.path.pathsep)

    paths.insert(0, '.')
    
    filePath = ''
    
    for path, ext in product(paths, exts):
        testPath = ''.join([os.path.join(path, name), ext])
        if os.path.exists(testPath):
            filePath = os.path.abspath(testPath)
            break        
            
    if filePath:
        print(filePath)
    else:
        print('which.py: no {} in ({})'.format(name, os.path.pathsep.join(paths)), file=sys.stderr)
        return ERROR_NOTFOUND
    return ERROR_NOERROR
    
    
    
if __name__ == '__main__':
    sys.exit(main(sys.argv))
    