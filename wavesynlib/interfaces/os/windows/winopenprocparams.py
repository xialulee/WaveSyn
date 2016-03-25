# -*- coding: utf-8 -*-
"""
Created on Thu Sep 10 14:01:43 2015

@author: xialulee
"""
import sys
from procparam import query
from wavesynlib.interfaces.os.windows.shell.winopen   import winopen

def split(commandLine):
    commandLine += ' '
    params = []
    start  = -1
    index  = 0
    length = len(commandLine)
    while True:
        if index >= length:
            break
        char = commandLine[index]
        if char == '"':
            start = index + 1
            for i in range(start, length):
                if commandLine[i] == '"':
                    params.append(commandLine[start:i])
                    index = i + 1
                    break
        elif char == ' ':
            index += 1
        else:
            start = index
            for i in range(start+1, length):
                if commandLine[i] == ' ':
                    break
            index = i + 1
            params.append(commandLine[start:i])
    return params


def main():
    procName     = sys.argv[1]
    commandLines = query(procName)
    for commandLine in commandLines:
        params = split(commandLine)
        for param in params[1:]:
            try:
                winopen(param)
            except:
                pass
            
            
if __name__ == '__main__':
    main()
    
