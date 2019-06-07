# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 21:57:39 2019

@author: Feng-cong Li
"""

import sys
import hashlib
from argparse import ArgumentParser



def calc_file_sha256(given_file):
    m = hashlib.sha256()
    while True:
        data = given_file.read(1048576)
        if not data:
            break
        m.update(data)
    return m.hexdigest()



def main():
    parser = ArgumentParser(description='''''')
    parser.add_argument(
        'files',
        metavar='FILE',
        type=str,
        nargs='*',
        help='')
    
    args = parser.parse_args()
    
    for file_path in args.files:
        if file_path == '-':
            result = calc_file_sha256(sys.stdin)
        else:
            with open(file_path, 'rb') as f:
                result = calc_file_sha256(f)
        print(f'{result}{" "*2}{file_path}')
    
    
    
if __name__ == '__main__':
    sys.exit(main())