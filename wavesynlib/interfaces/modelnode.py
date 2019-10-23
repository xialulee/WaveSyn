import os
from os.path import dirname, join
import hy
try:
    from wavesynlib.interfaces.hynode import *
except hy.errors.HyCompileError:
    node_path = join(dirname(__file__), 'hynode.hy')
    os.system(f'hyc {node_path}')
    from wavesynlib.interfaces.hynode import *
