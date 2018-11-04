# -*- coding: utf-8 -*-
"""
Created on Sun Jul 15 17:27:43 2018

@author: Feng-cong Li
"""

import locale
import subprocess as sp
import os

from pathlib import Path



def unpack(rar_file:(str, Path), dir_path:(str, Path))->(str, str):
    p = sp.Popen(['unrar', 'x', rar_file, dir_path], stdout=sp.PIPE, stderr=sp.PIPE)
    outs, errs = p.communicate()
    outs = outs.decode(locale.getpreferredencoding())
    errs = errs.decode(locale.getpreferredencoding())
    return outs, errs



def list_content(path):
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



def get_content_tree(contents_list):
    root = {'children':{}}
    for item in contents_list:
        dir_ptr = root
        path = item['Name']
        path_items = path.split(os.path.sep)
        for path_item in path_items[:-1]:
            if path_item not in dir_ptr['children']:
                dir_ptr['children'][path_item] = {'children':{}}
            dir_ptr = dir_ptr['children'][path_item]

        path_item = path_items[-1]            
        if path_item not in dir_ptr['children']:
            dir_ptr['children'][path_item] = {}
        new_node = dir_ptr['children'][path_item]
        if item['Type'] == 'Directory' and 'children' not in new_node:
            new_node['children'] = {}
           
        for key in item:
            if key == 'Name':
                new_node['path'] = item['Name']
                continue
            new_node[key] = item[key]
    return root