# -*- coding: utf-8 -*-
"""
Created on Tue Dec 29 12:14:21 2015

@author: Feng-cong Li
"""
import subprocess as sp

def execute(command):
    ps  = sp.Popen(['powershell', '-Command', command], stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
    stdout, stderr  = ps.communicate()
    errorlevel      = ps.wait()
    return (stdout, stderr, errorlevel)