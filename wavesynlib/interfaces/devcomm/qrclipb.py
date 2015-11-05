# -*- coding: utf-8 -*-
"""
Created on Thu Nov 05 12:26:16 2015

@author: Feng-cong Li
"""
from __future__ import print_function

import barcode
import platform
from cStringIO import StringIO

if platform.system() == 'Windows':
    from wavesynlib.interfaces.windows.clipb import clipb2stream
    
import sys    
import getopt
    
    
ERROR_NOERROR, ERROR_PARAM = range(2)    
    
def main(argv):
    try:
        opts, args = getopt.getopt(argv[1:],\
            'd:e:s:',\
            ['decode=', 'encode=', 'size=']
        )
    except getopt.GetoptError, err:
        print(str(err), file=sys.stderr)
        sys.exit(ERROR_PARAM)
        
    code = None
    for o, a in opts:
        if o in ('-d', '--decode'):
            code = a
        
        
    stream = StringIO()
    clipb2stream(stream, None, code, None)
    stream.seek(0)
    origStdin = sys.stdin
    sys.stdin = stream
    argv.append('--stdin')
    argv.append('--wintitle=WaveSyn-QrClipb')
    barcode.main(argv)
    sys.stdin = origStdin
    
    
if __name__ == '__main__':
    main(sys.argv)