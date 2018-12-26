# -*- coding: utf-8 -*-
"""
Created on Wed Dec 26 21:05:55 2018

@author: Feng-cong Li
"""

import os
from pathlib import Path
import hy
try:
    from wavesynlib.interfaces.os.windows.processes.hynode import Processes
except hy.errors.HyCompileError:
    hy_path = Path(__file__).parent / 'hynode.hy'
    os.system(f'hyc {hy_path}')
    from wavesynlib.interfaces.os.windows.processes.hynode import Processes
