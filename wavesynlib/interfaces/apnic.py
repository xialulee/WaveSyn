# -*- coding: utf-8 -*-
"""
Created on Sat Aug  4 18:47:28 2018

@author: Feng-cong Li
"""

from urllib.request import urlopen



class AllocationAndAssignmentReports:
    '''\
Load data from http://ftp.apnic.net/apnic/stats/apnic/delegated-apnic-latest.
File format see ftp://ftp.apnic.net/pub/apnic/stats/apnic/README.TXT.'''
    def __init__(self, fileobj):
        self.__comments = []
        self.__version = None
        self.__summaries = []
        self.__records = []
        self._load(fileobj)
        
        
    @property
    def comment(self):
        return ''.join(self.__comments)
    
    
    @property
    def version(self):
        return self.__version
    
    
    @property
    def summaries(self):
        return self.__summaries
    
    
    @property
    def records(self):
        return self.__records
    
    
    def _load(self, fileobj):
        while True:
            line = fileobj.readline().decode()
            if line.startswith('#'):
                self.__comments.append(line)
            else:
                break
            
        # The first line after comments is the version line of the header.
        fields = line.split('|')
        field_names = ['version', 'registry', 'serial', 'records', 'startdate', 'enddate', 'UTCoffset']
        self.__version = dict(zip(field_names, fields))
        
        # Summary lines
        field_names = ['registry', 'type', 'count', 'summary']
        while True:
            line = fileobj.readline().decode()
            fields = line.split('|')
            if fields[1]!='*' or fields[3]!='*':
                break
            self.__summaries.append(dict(zip(field_names, [v for v in fields if v!='*'])))
            
        # Records
        field_names = ['registry', 'cc', 'type', 'start', 'value', 'date', 'status']
        while True:
            if not line:
                break
            fields = line.split('|')[:len(field_names)]
            self.__records.append(dict(zip(field_names, fields)))
            line = fileobj.readline().decode()
    
    
    
def get_allocation_and_assignment_reports():
    page = urlopen('http://ftp.apnic.net/apnic/stats/apnic/delegated-apnic-latest')
    reports = AllocationAndAssignmentReports(page)
    page.close()
    return reports