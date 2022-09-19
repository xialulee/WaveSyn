import inspect

from wavesynlib.languagecenter.wavesynscript import ModelNode
from wavesynlib.languagecenter.python.utils import get_module_path



class BaseToolboxNode(ModelNode):
    def __init__(self, *args, **kwargs) -> None:
        self.__toolbox_name = kwargs.pop("toolbox_name")
        super().__init__(*args, **kwargs)

    @property
    def _toolbox_name(self):
        return self.__toolbox_name


    @property
    def toolbox_package_path(self):
        """Return the package path of this toolbox node. """
        return self.module_path.parent



class BaseXLWingsUDFNode(ModelNode):
    def get_module_path(self):
        """Get the module path of the xlwings UDF."""
        raise NotImplementedError("get_module_path not implemented.")
