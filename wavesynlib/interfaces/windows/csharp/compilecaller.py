# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 19:57:41 2015

@author: Feng-cong Li
"""
from __future__ import print_function

import os
import sys
from os.path import abspath, dirname, join
import inspect
import subprocess
import tempfile
from tkFileDialog import askopenfilename, asksaveasfilename
from Tkinter import Tk
from wavesynlib.languagecenter.utils import auto_subs

def get_my_dir():
    return abspath(dirname(inspect.getfile(inspect.currentframe())))

    
callerCode = '''
using System;

class ScriptCaller
{ 
  static void Main()
  {
    System.Diagnostics.Process.Start("$scriptPath"); 
  }
} 

'''

def compileCaller(scriptPath, exeFileName):
    codeFile = tempfile.NamedTemporaryFile(delete=False)
    print(auto_subs(callerCode), file=codeFile)
    codeFile.close()
    
    try:    
        powershell = subprocess.Popen(['powershell.exe',
            '-ExecutionPolicy', 'Unrestricted',
            join(get_my_dir(), 'cscompiler.ps1'),
            codeFile.name,
            exeFileName,
            'System.dll'
        ])
        ret = powershell.wait()
    finally:
        os.remove(codeFile.name)
    return ret
        
        
def main(argv):
    scriptPath  = askopenfilename()
    exeFileName = asksaveasfilename(filetypes=[('Executable', '*.exe')])
    if not os.path.splitext(exeFileName)[1]:
        exeFileName += '.exe'
    compileCaller(scriptPath, exeFileName)
    return 0
    
if __name__ == '__main__':
    root = Tk()
    root.withdraw()
    sys.exit(main(sys.argv))