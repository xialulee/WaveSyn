# -*- coding: utf-8 -*-
"""
Created on Sun Mar 18 21:16:32 2018

@author: Feng-cong Li
"""

import os
import tempfile
import subprocess



def main(argv):
    fd, filename = tempfile.mkstemp(text=True)
    with os.fdopen(fd, 'w') as f:
        # Close the temp file and consequently the external editor can edit
        # it without limitations.
        pass
    subprocess.call(['gvim', filename])
    with open(filename, 'r') as f:
        for line in f:
            print(line, end='')
    os.remove(filename)
    
    
    
if __name__ == '__main__':
    main(None)



# Powershell Example:
# python -c $(wsvimbufp | Out-String)
