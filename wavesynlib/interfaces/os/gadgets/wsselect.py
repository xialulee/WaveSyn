# -*- coding: utf-8 -*-
"""
Created on Wed Mar 01 21:54:34 2017

@author: Feng-cong Li
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
import sys
from collections import OrderedDict


def main(argv):    
    argv = argv[1:]

    while True:
        try:
            s = raw_input()
        except EOFError:
            break
        record = json.loads(s)
        od = OrderedDict()
        for arg in argv:
            od[arg] = record.get(arg, '')
        print(json.dumps(od))


if __name__ == '__main__':
    sys.exit(main(sys.argv))