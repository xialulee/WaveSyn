# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 16:10:33 2015

@author: Feng-cong Li
"""
import os
import pathlib
from setuptools import setup, find_packages

selfpath = pathlib.Path(os.path.realpath(__file__))
dirpath = selfpath.parent

try:
    import tkinter
    from tkinter.filedialog import askdirectory
    root = tkinter.Tk()
    root.withdraw()
    def ask_config_dir():
        return askdirectory(title='Select the directory for storing config, cache, and history files.')
except:
    def ask_config_dir():
        return input('Please input the path of the directory for storing config, cache, and history files:\n')

specpath = ask_config_dir()

with open(dirpath / 'wavesynlib' / 'path.txt', 'w') as f:
    f.write(specpath)
    
setup(
      name="wavesynlib",
      version="0.10",
      description="WaveSyn: A tool for radar waveform synthesis.",
      author="Feng-cong Li",
      url="https://github.com/xialulee/WaveSyn",
      packages= find_packages(),
      scripts=["scripts/launchwavesyn.py"],
      package_data = {
        # If any package contains *.json/png/pyw files, include them:
        # .m files for Matlab functions and scripts.
        # .ps1 files for PowerShell scripts.
        '': ['*.json', '*.png', '*.ico', '*.dll', '*.pyw', '*.ps1', '*.bat', '*.m', '*.txt']
      }
)
