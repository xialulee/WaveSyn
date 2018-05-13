# -*- coding: utf-8 -*-
"""
Created on Sat Nov 07 15:20:19 2015

@author: Feng-cong Li
"""
from tkinter import Tk
from tkinter.filedialog import askdirectory, askopenfilenames
import sys
import getopt

ERROR_NOERROR, ERROR_PARAM, ERROR_NOSEL = range(3)

def usage():
    pass

def main(argv):
    try:
        opts, args = getopt.getopt(argv[1:],\
            'd',\
            ['dir', 'filetype=', 'typename=']\
        )
    except getopt.GetoptError as err:
        print(str(err), file=sys.stderr)
        usage()
        return ERROR_PARAM
        
    directory = False
    filetype  = ''
    typename  = ''
    for o, a in opts:
        if o in ('-d', '--dir'):
            directory = True
        if o in ('--filetype'):
            filetype = a
        if o in ('--typename'):
            typename = a
            
    root = Tk()
    root.withdraw()            
            
    path_list = None
    if directory:
        path_list = (askdirectory(),)
    else:
        param = {}
        if filetype:
            param['filetypes'] = [(typename, filetype)]
        path_list = askopenfilenames(**param)
        
    if not path_list:
        print('No file/directory selected.', file=sys.stderr)
    
    for path in path_list:
        print(path)
        
    return ERROR_NOERROR
    
    
if __name__ == '__main__':
    sys.exit(main(sys.argv))