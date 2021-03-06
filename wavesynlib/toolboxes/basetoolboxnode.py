from wavesynlib.languagecenter.wavesynscript import ModelNode



class BaseToolboxNode(ModelNode):
    def __init__(self, *args, **kwargs) -> None:
        self.__toolbox_name = kwargs.pop("toolbox_name")
        super().__init__(*args, **kwargs)

    @property
    def _toolbox_name(self):
        return self.__toolbox_name
