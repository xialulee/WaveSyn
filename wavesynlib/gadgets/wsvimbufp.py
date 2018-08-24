# -*- coding: utf-8 -*-
"""
Created on Sun Mar 18 21:16:32 2018

@author: Feng-cong Li
"""

import os
import sys
import getopt
import chardet
import tempfile
import subprocess



ERROR_NOERROR, ERROR_PARAM = range(2)



def detect_file_encoding(filename):
    detector = chardet.UniversalDetector()
    with open(filename, 'rb') as f:
        for line in f:
            detector.feed(line)
            if detector.done: break
        detector.close()
    return detector.result


def main(argv):
    try:
        opts, args = getopt.getopt(argv[1:],\
            'gc:',\
            ['gvim', 'tempext='])
    except getopt.GetoptError as err:
        print(str(err), file=sys.stderr)
        return ERROR_PARAM
    
    vim_name = 'vim'
    
    opt_list = []
    tempext = None
    for o, a in opts:
        if o in ('-g', '--gvim'):
            vim_name = 'gvim'
        elif o == '--tempext':
            ext = a
            if not ext.startswith('.'):
                ext = '.' + ext
            tempext = ext
        else:
            opt_list.append(o)
            if a:
                opt_list.append(a)
           
    is_stdin = False
    is_temp = True
    
    if args:
        if args[0] != '-':
            filename = args[0]
            is_temp = False
        else:
            is_stdin = True
            
    if not is_temp:
        filename = args[0]
    else:
        mkstemp_kwargs = {'text':True}
        if tempext:
            mkstemp_kwargs['suffix'] = tempext
        fd, filename = tempfile.mkstemp(**mkstemp_kwargs)
        args.append(filename)        
        with os.fdopen(fd, 'w') as f:
            # Close the temp file and consequently the external editor can edit
            # it without limitations.
            if is_stdin:
                f.write(sys.stdin.read())
                
    opt_list.append(filename)
    subprocess.call([vim_name, *opt_list])
    
    detect_result = detect_file_encoding(filename)
    # If multiple files are given, only output the content of the first file. 
    with open(filename, 'r', encoding=detect_result['encoding']) as f:
        for line in f:
            print(line, end='')
    if is_temp:
        os.remove(filename)
    return ERROR_NOERROR
    
    
    
if __name__ == '__main__':
    main(sys.argv)



# Powershell Example:
# python -c $(wsvimbufp -g | Out-String)
# using -g is highly recommanded on Windows OS.
