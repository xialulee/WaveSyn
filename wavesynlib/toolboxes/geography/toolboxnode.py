from wavesynlib.languagecenter.wavesynscript import ModelNode

from ..basetoolboxnode import BaseToolboxNode


class ToolboxNode(BaseToolboxNode):
    def __init__(self, *args, **kwargs):
        self.xlwings_udf = ModelNode(
            is_lazy=True,
            module_name=f"{self.toolbox_package_path}.xlwingsudf", 
            class_name="XLWingsUDFNode")
        super().__init__(self, *args, **kwargs)
