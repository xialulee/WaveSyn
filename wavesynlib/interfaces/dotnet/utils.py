# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 22:57:24 2017

@author: Feng-cong Li
"""

import os
from pathlib import Path
import hy
try:
    from wavesynlib.interfaces.dotnet.hyutils import *
except hy.errors.HyCompilerError:
    hy_path = Path(__file__).parent / 'hyutils.hy'
    os.system(f'hyc {hy_path}')
    from wavesynlib.interfaces.dotnet.hyutils import *

