from wavesynlib.languagecenter.wavesynscript import ModelNode

from ..basetoolboxnode import BaseToolboxNode



class BingMapsNode(ModelNode):
    def display_multiple_points(self, names, lla=None, wgs84=None):
        from . import bingmaps
        bingmaps.display_multiple_points(names, lla=lla, wgs84=wgs84)



class ToolboxNode(BaseToolboxNode):
    def __init__(self, *args, **kwargs):
        self.xlwings_udf = ModelNode(
            is_lazy=True,
            module_name=f"{self.toolbox_package_path}.xlwingsudf", 
            class_name="XLWingsUDFNode")

        self.bingmaps = ModelNode(
            is_lazy=True,
            class_object=BingMapsNode)
        super().__init__(self, *args, **kwargs)
