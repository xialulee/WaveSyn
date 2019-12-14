from wavesynlib.languagecenter.wavesynscript import ModelNode, Scripting
from .systemshellmode import SystemShell
from .basemode import BaseMode



class ExtraModesNode(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        mode_classes = [SystemShell]
        self.__modes = []
        for mode_class in mode_classes:
            if not issubclass(mode_class, BaseMode):
                raise TypeError("The given class of mode node is not subclass of BaseMode.")
            mode_object = mode_class()
            setattr(self, mode_object.info.name, mode_object)
            self.__modes.append(mode_object)


    def _get_mode(self, code):
        for mode in self.__modes:
            if mode.test(code):
                return mode
        raise TypeError('The mode of the code is unrecognizable.')


    def translate(self, code):
        right_mode = self._get_mode(code)
        return right_mode.translate(code)
            

    @Scripting.printable
    def run(self, code):
        right_mode = self._get_mode(code)
        self.root_node.stream_manager.write(f'''
WaveSyn:
The mode of the code is recognized as {right_mode.info.name}. 
The actual code executed is listed as follows:
''', 'TIP') # To Do: The output is stored in ...
        right_mode.translate_and_run(code)
