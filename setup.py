# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 16:10:33 2015

@author: Feng-cong Li
"""

from setuptools import setup, find_packages
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
        '': ['*.json', '*.png', '*.pyw']
      }
)