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
        return self.module_path.parent
