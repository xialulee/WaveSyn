# -*- coding: utf-8 -*-
"""
Created on Wed Mar 01 22:26:26 2017

@author: Feng-cong Li
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
import sys
from collections import OrderedDict


decode = json.JSONDecoder(object_pairs_hook=OrderedDict).decode


def main(argv):
    nr = 0
    while True:
        try:
            s = raw_input()
        except EOFError:
            break
        
        # see http://stackoverflow.com/a/6921760
        record = decode(s)
        if nr == 0:
            print('\t'.join(record.keys()))
            print('-'*25)
        print('\t'.join([str(value) for value in record.values()]))
        nr += 1
        
        
if __name__ == '__main__':
    sys.exit(main(sys.argv))
        