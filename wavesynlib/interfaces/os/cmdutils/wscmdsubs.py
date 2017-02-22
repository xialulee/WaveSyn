# -*- coding: utf-8 -*-
"""
Created on Wed Feb 22 22:08:37 2017

@author: Feng-cong Li
"""
from __future__ import print_function, division, unicode_literals

import sys
from string import Formatter
from subprocess import Popen, PIPE, call


class CmdFormatter(Formatter):        
    def get_value(self, expr, args=None, kwargs=None):
        p = Popen(['cmd', '/c', expr], stdout=PIPE)
        result = p.communicate()[0]
        result = result.replace('\r\n', '')
        return result
        


if __name__ == '__main__':
    args = ['cmd', '/c']
    for arg in sys.argv[1:]:
        args.append(CmdFormatter().format(arg))
    
    retcode = call(args)
    sys.exit(retcode)
