# -*- coding: utf-8 -*-
"""
Created on Wed Mar 01 13:18:42 2017

@author: xialulee
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
import ast
import re


type_cast = {
    'd': int,
    'i': int, 
    'o': int, 
    'u': int,
    'x': int,
    'X': int,
    'f': float,
    'e': float,
    'E': float,
    'g': float,
    'G': float,
    'c': int,
    's': lambda x: x
}


def main(argv):
    fmt = argv[1]
    fmt = fmt.replace('"', r'\"')
    fmt = fmt.replace("'", r"\'")
    fmt = ast.literal_eval("'{}'".format(fmt))
    specs = re.findall(r'%\+?(?:\d*\.?\d*)?([diouxXfeEgGcs])', fmt)
    args = []
    for spec, val in zip(specs, argv[2:]):
        args.append(type_cast[spec](val))
    print(fmt % tuple(args))
        
        
if __name__ == '__main__':
    sys.exit(main(sys.argv))