# -*- coding: utf-8 -*-
"""
Created on Sun Aug 28 00:38:46 2016

@author: Feng-cong Li
"""

import os
from os.path import dirname, join
import hy
try:
    from wavesynlib.fileutils.hyutils import *
except hy.errors.HyCompilerError:
    utils_path = join(dirname(__file__), 'hyutils.hy')
    os.system(f'hyc {utils_path}')
    from wavesynlib.fileutils.hyutils import *
