from wavesynlib.languagecenter.wavesynscript import ModelNode
from ..basetoolboxnode import BaseToolboxNode



class ToolboxNode(BaseToolboxNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.band_info = ModelNode(
            is_lazy = True,
            module_name=f"{self.toolbox_package_path}.bands.modelnode",
            class_name="BandInfo")


    