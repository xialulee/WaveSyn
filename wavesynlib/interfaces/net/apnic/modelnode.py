# -*- coding: utf-8 -*-
"""
Created on Tue Aug  7 01:40:48 2018

@author: Feng-cong Li
"""

import platform
from urllib.request import urlopen
from email.utils import parsedate
from datetime import datetime

from wavesynlib.languagecenter.wavesynscript import ModelNode, WaveSynScriptAPI
from wavesynlib.interfaces.net.apnic.utils import AllocationAndAssignmentReports

CACHENAME = '1F69F0F3-F874-4B25-AF97-456A4C5150CE.txt'



class APNIC(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
    def __get_reports_path(self, verbose=False):
        with urlopen('http://ftp.apnic.net/apnic/stats/apnic/delegated-apnic-latest') as response:
            page_time = datetime(*parsedate(response.info()['Last-Modified'])[:6])
            if verbose:
                print(f"APNIC Last-Modified: {page_time}.")
            cache_path = self.root_node.get_cache_path() / CACHENAME        
            if (not cache_path.exists()) or \
                datetime.fromtimestamp(cache_path.stat().st_mtime)<page_time:
                if verbose:
                    print("APNIC cache obsolete. Refreshing...")
                with open(cache_path, 'w') as f:
                    for line in response:
                        f.write(line.decode())
                if verbose:
                    print("APNIC cache refreshing complete.")
            else:
                if verbose:
                    print("APNIC cache is up to date.")
            return cache_path
        

    @WaveSynScriptAPI(thread_safe=True)    
    def get_reports(self, verbose=False):
        with open(self.__get_reports_path(verbose=verbose)) as f:
            return AllocationAndAssignmentReports(f)


    @WaveSynScriptAPI(thread_safe=True)
    def make_route_table(self, filter, gateway, script_file_add, script_file_delete, verbose=False):
        result = self.get_reports(verbose=verbose)
        df = result.records_as_dataframe
        df = df.query(filter)
        if platform.system() == "Windows":
            with open(script_file_add, "w") as fadd, \
                 open(script_file_delete, "w") as fdel:
                for row in df.itertuples():
                    print(f"route add {row.start} mask {row.mask} {gateway}", file=fadd)
                    print(f"route delete {row.start} mask {row.mask}", file=fdel)
        if verbose:
            print("Route table generated.")                    
