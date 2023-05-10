from pathlib import Path

from ..basetoolboxnode import BaseToolboxNode
from wavesynlib.languagecenter.wavesynscript import (
    Scripting, ModelNode, WaveSynScriptAPI, NodeDict, code_printer)


class ToolboxNode(BaseToolboxNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

