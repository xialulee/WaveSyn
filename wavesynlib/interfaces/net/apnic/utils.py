# -*- coding: utf-8 -*-
"""
Created on Sat Aug  4 18:47:28 2018

@author: Feng-cong Li
"""

from math import log2
from urllib.request import urlopen
import pandas



def _readline(fileobj):
    line = fileobj.readline()
    if isinstance(line, bytes):
        line = line.decode()
    return line



def _calc_ipv4_mask(value):
    value = int(value)
    i = int(log2(value))
    m = '1'*(32-i)+'0'*i 
    mask = []
    for k in range(4):
        mask.append(str(int(m[(k*8):(k*8+8)], base=2)))
    return '.'.join(mask)



def _calc_ipv4_int(ip):
    ip = ip.split(".")
    result = 0
    for s, p in zip(ip, (24, 16, 8, 0)):
        result += int(s) << p
    return result



class AllocationAndAssignmentReports:
    '''\
Load data from http://ftp.apnic.net/apnic/stats/apnic/delegated-apnic-latest.
File format see ftp://ftp.apnic.net/pub/apnic/stats/apnic/README.TXT.'''
    def __init__(self, fileobj):
        self.__comments = []
        self.__version = None
        self.__summaries = []
        self.__records = []
        self.__dataframe = None
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


    @property
    def records_as_dataframe(self):
        if self.__dataframe is None:
            self.__dataframe = pandas.DataFrame(self.__records)
        return self.__dataframe


    def ip_search(self, ip):
        ip_int = _calc_ipv4_int(ip)
        return self.records_as_dataframe.query(f"start_int <= {ip_int} <= stop_int").iloc[0]
    
    
    def _load(self, fileobj):
        while True:
            line = _readline(fileobj)
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
            line = _readline(fileobj)
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
            fields[-1] = fields[-1].strip()
            record = dict(zip(field_names, fields))
            if record['type'] == 'ipv4':
                value = int(record["value"])
                record["mask"] = _calc_ipv4_mask(value)
                record["start_int"] = start_int = _calc_ipv4_int(record["start"])
                record["stop_int"]  = start_int + value -1
            self.__records.append(record)
            line = _readline(fileobj)
    
    
    
def get_allocation_and_assignment_reports():
    with urlopen('http://ftp.apnic.net/apnic/stats/apnic/delegated-apnic-latest') as page:
        reports = AllocationAndAssignmentReports(page)
    return reports