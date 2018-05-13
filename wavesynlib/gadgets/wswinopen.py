# -*- coding: utf-8 -*-
"""
Created on Fri Mar 16 19:06:59 2018

@author: Feng-cong Li
"""
import sys
import platform
sysname = platform.system()

if sysname == 'Windows':
    from wavesynlib.interfaces.os.windows.shell.winopen import winopen
elif sysname == 'Linux':
    from wavesynlib.interfaces.os.linux.shell.winopen import winopen



if __name__ == '__main__':
    path = sys.argv[1]
    try:
        winopen(path)
        sys.exit(0)
    except ValueError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
