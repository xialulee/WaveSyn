# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 21:57:39 2019

@author: Feng-cong Li
"""

import sys
from argparse import ArgumentParser

from wavesynlib.fileutils import calc_hash



calc_file_sha256 = lambda given_file: calc_hash(given_file, 'sha256')



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