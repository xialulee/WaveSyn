# -*- coding: utf-8 -*-
"""
Created on Tue Aug  7 01:40:48 2018

@author: Feng-cong Li
"""

from urllib.request import urlopen
from email.utils import parsedate
from datetime import datetime

from wavesynlib.languagecenter.wavesynscript import ModelNode
from wavesynlib.interfaces.net.apnic.utils import AllocationAndAssignmentReports

CACHENAME = '1F69F0F3-F874-4B25-AF97-456A4C5150CE.txt'



class APNIC(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
    def __get_reports_path(self):
        with urlopen('http://ftp.apnic.net/apnic/stats/apnic/delegated-apnic-latest') as response:
            page_time = datetime(*parsedate(response.info()['Last-Modified'])[:6])
            
            cache_path = self.root_node.get_cache_path() / CACHENAME        
            if (not cache_path.exists()) or \
                datetime.fromtimestamp(cache_path.stat().st_mtime)<page_time:

                with open(cache_path, 'w') as f:
                    for line in response:
                        f.write(line.decode())
            return cache_path
        
        
    def get_reports(self):
        with open(self.__get_reports_path()) as f:
            return AllocationAndAssignmentReports(f)