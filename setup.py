# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 16:10:33 2015

@author: Feng-cong Li
"""
import os
import pathlib
from setuptools import setup, find_packages, Extension
import numpy
from Cython.Build import cythonize

selfpath = pathlib.Path(os.path.realpath(__file__))
dirpath = selfpath.parent
specpath = pathlib.Path.home() / ".wavesyndata"
if not specpath.exists():
    specpath.mkdir()

with open(dirpath / 'wavesynlib' / 'path.txt', 'w') as f:
    f.write(str(specpath))
    
setup(
      name="wavesynlib",
      version="0.10",
      description="WaveSyn: A tool for radar waveform synthesis.",
      author="Feng-cong Li",
      url="https://github.com/xialulee/WaveSyn",
      packages= find_packages(),
      scripts=["scripts/launchwavesyn.py"],
      ext_modules=cythonize("wavesynlib/fileutils/photoshop/packbits.pyx"),
      include_dirs=[numpy.get_include()],
      zip_safe=False,
      package_data = {
        # If any package contains *.json/png/pyw files, include them:
        # .m files for Matlab functions and scripts.
        # .ps1 files for PowerShell scripts.
        '': ['*.json', '*.png', '*.psd', '*.ico', '*.dll', '*.pyw', 
             '*.hy', '*.ps1', '*.bat', '*.m', '*.txt']
      }
)
