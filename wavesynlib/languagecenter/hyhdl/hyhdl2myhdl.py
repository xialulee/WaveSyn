# -*- coding: utf-8 -*-
"""
Created on Tue Jan 15 21:19:41 2019

@author: Feng-cong Li
"""

import sys
import re
from subprocess import Popen, PIPE



def main(args):
    hy_path = args[1]
    py_path = args[2]
    hy2py = Popen(['hy2py', hy_path], stdout=PIPE)
    out, err = hy2py.communicate()
    if err:
        print(err)
    if out:
        out = re.sub(rb"(?:[_a-zA-Z][_a-zA-Z0-9]*)\s*=\s*['\"]HYHDL-STMT-RETVAL['\"]", b"pass", out)
    with open(py_path, 'wb') as py_file:
        py_file.write(out)
    
    
    
if __name__ == "__main__":
    main(sys.argv)
