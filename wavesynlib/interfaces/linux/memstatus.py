# -*- coding: utf-8 -*-
"""
Created on Thur Feb 25 2016

@author: Feng-cong Li
"""
from __future__ import division, print_function, unicode_literals

def get_memory_usage():
    with open('/proc/meminfo') as f:
        mem_total = int(f.readline().split()[1])
        mem_free = int(f.readline().split()[1])
        mem_available = int(f.readline().split()[1])
        return int(mem_available / mem_total * 100)

