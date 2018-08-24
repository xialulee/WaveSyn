# -*- coding: utf-8 -*-
"""
Created on Wed Feb 22 22:08:37 2017

@author: Feng-cong Li
"""
import sys
from subprocess import Popen, PIPE, call


    
def subs(arg):
    if arg.startswith('$') and (not arg.startswith('$$')):
        p = Popen(['cmd', '/c', arg[1:]], stdout=PIPE)
        result = p.communicate()[0]
        result = result.decode('mbcs')
        result = result.replace('\r\n', '')
        return result
    else:
        return arg
        


if __name__ == '__main__':
    args = ['cmd', '/c']
    for arg in sys.argv[1:]:
        args.append(subs(arg))
    
    retcode = call(args)
    sys.exit(retcode)
