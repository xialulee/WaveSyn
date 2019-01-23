# -*- coding: utf-8 -*-
"""
Created on Tue Jan 15 21:19:41 2019

@author: Feng-cong Li
"""

import sys
import re
from subprocess import Popen, PIPE



def convert(out_stream, in_stream):
    hdlcode = b'''\
(require [wavesynlib.languagecenter.hyhdl.macros [HYHDL-INIT]])
(HYHDL-INIT)
'''    
    hdlcode += in_stream.read()
    hy2py = Popen(['hy2py', '-'], stdin=PIPE, stdout=PIPE)
    out, err = hy2py.communicate(hdlcode)
    if hy2py.returncode:
        return hy2py.returncode, err
    out = re.sub(rb"(?:[_a-zA-Z][_a-zA-Z0-9]*)\s*=\s*['\"]HYHDL-STMT-RETVAL['\"]", b"pass", out)    
    out_stream.write(out)
    return 0, ""



def main(args):
    hy_path = args[1]
    py_path = args[2]
    
    with open(hy_path, 'rb') as hy_file, open(py_path, 'wb') as py_file:
        retcode, stderr = convert(py_file, hy_file)
    if retcode:
        print(stderr)
        return retcode
    else:
        return 0

    
    
if __name__ == "__main__":
    sys.exit(main(sys.argv))
