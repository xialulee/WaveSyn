# -*- coding: utf-8 -*-
"""
Created on Thu Mar 02 15:54:06 2017

@author: Feng-cong Li
"""

from __future__ import print_function, division, unicode_literals

import sys
import getopt
#from comtypes import client
from wavesynlib.interfaces.os.windows.wmi import WQL

from wavesynlib.languagecenter.datatypes import Table


def main(argv):
    try:
        opts, args = getopt.getopt(argv[1:], \
            '',\
            ['jsontable']\
        ) # TODO
    except getopt.GetoptError as err:
        print(str(err), file=sys.stderr)
        #usage()
        return 1
        
    json_output = False
    for o, a in opts:
        if o == '--jsontable':
            json_output = True      
        
    
    wql_str = args[0]
#    loc = client.CreateObject('WbemScripting.SWbemLocator')
#    svc = loc.ConnectServer('.', 'root\\cimv2')
#    items = svc.ExecQuery(wql_str)
    wql = WQL()
    items = wql.query(wql_str)
    flag = True

    head = []    
    table = Table(head)
    
    for item in items:
        row = []
        for prop in item.Properties_:
            if flag:
                head.append(prop.Name)
            row.append(prop.Value)
        if flag:
            table.head = head
            flag = False
            if not json_output:
                table.print_head()
                print('-'*25)
        table.print_row(row, lang='json' if json_output else 'plain')
            
            
if __name__ == '__main__':
    sys.exit(main(sys.argv))