#!/usr/bin/env ipy
# -*- coding: utf-8 -*-
# 2015.01.31 PM 04:30 Created
# procparam.py
# xialulee


import sys
import platform


wqlStringTemplate   = 'select commandline from win32_process where name="{0}"'

def ironpythonMain(wqlString):    
    import clr
    clr.AddReference('System.Management')
    from System.Management import SelectQuery, ManagementObjectSearcher
    
    q = SelectQuery(wqlString)
    s = ManagementObjectSearcher(q)
    
    for i in s.Get():
        print i['commandline']    
    
    
def cpythonMain(wqlString):
    from win32com.client import Dispatch
    computerName    = '.'
    locator         = Dispatch('WbemScripting.SWbemLocator')
    server          = locator.ConnectServer(computerName, r'root\cimv2')
    q               = server.ExecQuery(wqlString)
    for i in q:
        print i.commandline
        
        
def main():
    wqlString   = wqlStringTemplate.format(sys.argv[1])
    try:
        globals()[platform.python_implementation().lower() + 'Main'](wqlString)
    except KeyError:
        sys.stderr.write('Not supported Python implementation.\n')
        sys.exit(1)
        
        
if __name__ == '__main__':
    main()        