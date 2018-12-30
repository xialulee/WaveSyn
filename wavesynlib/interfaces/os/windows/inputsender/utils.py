# -*- coding: utf-8 -*-
"""
Created on Sun Dec 30 22:22:35 2018

@author: Feng-cong Li
"""

import os
from pathlib import Path
import hy
try:
    from wavesynlib.interfaces.os.windows.inputsender.hyutils import *
except hy.errors.HyCompileError:
    hy_path = Path(__file__).parent / 'hyutils.hy'
    os.system(f'hyc {hy_path}')
    from wavesynlib.interfaces.os.windows.inputsender.hyutils import *
