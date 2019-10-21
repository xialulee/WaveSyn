# -*- coding: utf-8 -*-
"""
Created on Mon Oct  1 22:48:35 2018

@author: Feng-cong Li
"""

import os
from os.path import dirname, join
import hy
try:
    from wavesynlib.interfaces.os.windows.shell.windowhandlegetter.hyutils import *
except hy.errors.HyCompileError:
    hy_path = join(dirname(__file__), 'hyutils.hy')
    os.system(f'hyc {hy_path}')
    from wavesynlib.interfaces.os.windows.shell.windowhandlegetter.hyutils import *