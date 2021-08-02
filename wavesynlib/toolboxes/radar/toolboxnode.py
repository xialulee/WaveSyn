from wavesynlib.languagecenter.wavesynscript import ModelNode
from ..basetoolboxnode import BaseToolboxNode



class ToolboxNode(BaseToolboxNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_lazy_local_node(
            "band_info", 
            ".bands.modelnode", 
            "BandInfo")
