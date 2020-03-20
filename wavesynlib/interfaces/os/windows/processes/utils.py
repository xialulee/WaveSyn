# -*- coding: utf-8 -*-
"""
Created on Sun Mar 05 21:44:05 2017

@author: Feng-cong Li
"""

import os
from pathlib import Path
import hy
try:
    from wavesynlib.interfaces.os.windows.processes.hyutils \
        import singleton, get_pid_from_hwnd, run_as_admin
except hy.errors.HyCompileError:
    hy_path = Path(__file__).parent / 'hyutils.hy'
    os.system(f'hyc {hy_path}')
    from wavesynlib.interfaces.os.windows.processes.hyutils \
        import singleton, get_pid_from_hwnd, run_as_admin
