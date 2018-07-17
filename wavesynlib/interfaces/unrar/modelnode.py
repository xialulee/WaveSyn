# -*- coding: utf-8 -*-
"""
Created on Sun Jul 15 17:28:37 2018

@author: Feng-cong Li
"""
import locale
import subprocess as sp



def list_contents(path):
    p = sp.Popen(['unrar', 'lta', path], stdout=sp.PIPE, stderr=sp.PIPE)
    outs, errs = p.communicate()
    outs = outs.decode(locale.getpreferredencoding())
    results = []
    for line in outs.split('\n'):
        line = line.strip()
        if line.startswith('Name:'):
            results.append({'Name':line[len('Name:'):].strip()})
        else:
            pieces = line.split(':', maxsplit=1)
            if len(pieces)==2:
                key, value = [p.strip() for p in pieces]
                if key in ('Type', 'Size', 'Packed size', 'mtime', 'Ratio', 'Attributes', 'CRC32'):
                    results[-1][key] = value
                
    return results
    
    
    
if __name__ == '__main__':
    import sys
    print(list_contents(sys.argv[1]))