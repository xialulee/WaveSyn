#!/usr/bin/env ipy
# -*- coding: utf-8 -*-
# 2015.01.31 PM 04:30 Created
# procparam.py
# xialulee


import sys
import platform




def ironpythonQuery(wqlString):    
    import clr
    clr.AddReference('System.Management')
    from System.Management import SelectQuery, ManagementObjectSearcher
    
    q = SelectQuery(wqlString)
    s = ManagementObjectSearcher(q)
    
    return [i['commandline'] for i in s.Get()]
    
    
def cpythonQuery(wqlString):
    from win32com.client import Dispatch
    computerName    = '.'
    locator         = Dispatch('WbemScripting.SWbemLocator')
    server          = locator.ConnectServer(computerName, r'root\cimv2')
    q               = server.ExecQuery(wqlString)

    return [i.commandline for i in q]

def query(procName):
    wqlStringTemplate   = 'select commandline from win32_process where name="{0}"'
    wqlString   = wqlStringTemplate.format(procName)
    return globals()[platform.python_implementation().lower() + 'Query'](wqlString)
        
        
def main():
    procName = sys.argv[1]
    try:
        result = query(procName)
        for item in result:
            print item
    except KeyError:
        sys.stderr.write('Not supported Python implementation.\n')
        sys.exit(1)
        
        
if __name__ == '__main__':
    main()        
