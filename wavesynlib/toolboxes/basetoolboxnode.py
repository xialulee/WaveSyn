import inspect

from wavesynlib.languagecenter.wavesynscript import ModelNode



class BaseToolboxNode(ModelNode):
    def __init__(self, *args, **kwargs) -> None:
        self.__toolbox_name = kwargs.pop("toolbox_name")
        super().__init__(*args, **kwargs)

    @property
    def _toolbox_name(self):
        return self.__toolbox_name


    @property
    def toolbox_package_path(self):
        return inspect.getmodule(self).__name__.rsplit('.', 1)[0]


    def add_lazy_local_node(self, node_name, module_name, class_name):
        if not module_name.startswith("."):
            module_name = f".{module_name}"
        setattr(
            self, 
            node_name, 
            ModelNode(
                is_lazy=True,
                module_name=f"{self.toolbox_package_path}{module_name}",
                class_name=class_name))
