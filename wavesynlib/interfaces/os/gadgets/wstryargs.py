# -*- coding: utf-8 -*-
"""
Created on Mon Mar 19 22:00:34 2018

@author: Feng-cong Li
"""

import sys



def main(argv):
    for idx, arg in enumerate(argv[1:]):
        print(f'{[idx]}: {{{arg}}}\n')
        
        
        
if __name__ == '__main__':
    main(sys.argv)