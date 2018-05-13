#!/usr/bin/env ipy
# -*- coding: utf-8 -*-
# 2015.01.31 PM 04:30 Created
# procparam.py
# Feng-cong Li

from __future__ import print_function

import sys
import platform
import getopt
from comtypes import client


platformName    = platform.python_implementation().lower() 

if platformName == 'cpython':
    def query(wqlString):
        from wavesynlib.interfaces.os.windows.wmi import WQL
        loc = client.CreateObject('WbemScripting.SWbemLocator')
        services = loc.ConnectServer('.')        
        q = WQL(services).query(wqlString, output_format='python')
        return [i['CommandLine'] for i in q]        
elif platformName == 'ironpython':
    def query(wqlString):
        import clr
        clr.AddReference('System.Management')
        from System.Management import SelectQuery, ManagementObjectSearcher
        
        q = SelectQuery(wqlString)
        s = ManagementObjectSearcher(q)
        
        return [i['commandline'] for i in s.Get()]   
else:
    raise NotImplementedError('This Python implementation is not supported.')



def queryByName(procName):
    wqlStringTemplate = 'select commandline from win32_process where name="{0}"'
    wqlString = wqlStringTemplate.format(procName)
    return query(wqlString)

def queryByPID(pid):
    wqlStringTemplate = 'select commandline from win32_process where processid={0}'
    wqlString = wqlStringTemplate.format(pid)
    return query(wqlString)
        

        
def main(argv):
    try:
        opts, args = getopt.getopt(argv[1:], '', ['name=', 'pid='])
    except getopt.GetoptError as err:
        print(str(err), file=sys.stderr)
        return 1
        
    for o, a in opts:
        if o in ('--name'):
            result = queryByName(a)
            for item in result:
                print(item)
            return 0
        elif o in ('--pid'):
            result = queryByPID(a)
            for item in result:
                print(item)
            return 0
        
        
if __name__ == '__main__':
    sys.exit(main(sys.argv))      
