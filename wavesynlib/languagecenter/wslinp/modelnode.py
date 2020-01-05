from wavesynlib.languagecenter.wavesynscript import ModelNode

import hy
from .engine import Engine



class WSLinp(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self, program, *files):
        engine = Engine()
        engine.run(program, *files)
