# -*- coding: utf-8 -*-
"""
Created on Thu Mar 02 15:54:06 2017

@author: Feng-cong Li
"""

from __future__ import print_function, division, unicode_literals

import sys
from comtypes import client

from wavesynlib.languagecenter.datatypes import Table


def main(argv):
    wql_str = argv[1]
    loc = client.CreateObject('WbemScripting.SWbemLocator')
    svc = loc.ConnectServer('.', 'root\\cimv2')
    items = svc.ExecQuery(wql_str)
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
            table.print_head()
            print('-'*25)
        table.print_row(row, lang='plain')
            
            
if __name__ == '__main__':
    sys.exit(main(sys.argv))