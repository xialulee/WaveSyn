# -*- coding: utf-8 -*-
"""
Created on Mon Dec 28 20:29:21 2015

@author: Feng-cong Li
"""

from   wavesynlib.interfaces.windows.clipboard import clipb
import re
import sys
from   cStringIO import StringIO

def main(argv):
    stream  = StringIO()
    clipb.clipb2stream(stream, mode='t', code='@', null=False)
    stream.seek(0)
    string  = stream.read()
    temp    = re.sub(r'(?<=[^ ])\n', ' \n', string)
    string  = re.sub(r'\n', '', temp)
    stream  = StringIO()
    stream.write(string)
    stream.seek(0)
    clipb.stream2clipb(stream, mode='t', code='@', tee=None, null=False)
    

if __name__ == '__main__':
    sys.exit(main(sys.argv))