#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 06 09:30:21 2015

@author: Feng-cong Li
"""

import os
import sys
import argparse
from pathlib import Path
import platform

from itertools import product
from collections import OrderedDict

from wavesynlib.interfaces.os.windows.shell.winopen import winopen
from wavesynlib.languagecenter.datatypes import Table

ERROR_NOERROR, ERROR_NOTFOUND, ERROR_PARAM = range(3)



def which(
        name: str,
        all_: bool = False,
        cwd: bool = False
    ) -> tuple[Path, ...]:
    p: Path = Path(name)
    suffixes: list[str] = p.suffixes
    ext: str = suffixes[-1] if suffixes else ''
    paths: list[str] = os.environ['PATH'].split(os.path.pathsep)
    if platform.system() == 'Windows':
        exts: list[str] = os.environ['PATHEXT'].split(os.path.pathsep)
        if ext:
            if ext.upper() not in [e.upper() for e in exts]:
                raise TypeError(f'The file {name} is not executable.')
            exts = [ext]
    else:
        if ext:
            exts = [ext]
        else:
            exts = ['']
    if cwd:
        paths.insert(0, '.')
    
    # Use OrderedDict as an Ordered Set.
    file_paths: OrderedDict[Path, bool] = OrderedDict()
    
    for path_str, ext in product(paths, exts):
        path: Path = Path(path_str)
        test_path: Path = path / f'{str(name)}{ext}'
        try:
            exists: bool = test_path.exists()
        except OSError:
            # happens when the path is not authorized to access.
            exists = False
        if exists:
            abs_test_path: Path = test_path.resolve()
            file_paths[abs_test_path] = True
            if not all_:
                break
    
    return tuple(file_paths)
    


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("name")
    parser.add_argument("-a", "--all",
                        dest="all_cmd", action="store_true")
    parser.add_argument("--winopen",
                        dest="wopen", action="store_true")
    parser.add_argument("--jsontable",
                        dest="json_output", action="store_true")
    parser.add_argument("--cwd",
                        dest="cwdfirst", action="store_true")
    parser.add_argument("--order",
                        dest="order",
                        action="store", type=int, default=-1)

    args = parser.parse_args(argv[1:])
        
    cmd_order = args.order
    all_cmd: bool = args.all_cmd
    if not all_cmd and cmd_order >= 0:
        all_cmd = True
    wopen: bool = args.wopen
    json_output: bool = args.json_output
    cwdfirst: bool = args.cwdfirst
    name = args.name

    try:
        file_paths: tuple[Path, ...] = which(
            name, all_=all_cmd, cwd=cwdfirst)
    except TypeError:
        print(
            f"The file {name} is not executable.", 
            file=sys.stderr)
        return ERROR_NOTFOUND
            
    if file_paths:
        table = Table(['order', 'path'])
        for order, file_path in enumerate(file_paths):
            if (cmd_order<0) or (cmd_order==order):
                if not json_output:
                    print(file_path)
                else:
                    table.print_row((order, str(file_path)))
                if wopen:
                    winopen(file_path)
    else:
        print(
            f'wswhich.py: no {name} in ({os.environ["PATH"]})',
            file=sys.stderr)
        return ERROR_NOTFOUND
    return ERROR_NOERROR
    
    
    
if __name__ == '__main__':
    sys.exit(main(sys.argv))
    
