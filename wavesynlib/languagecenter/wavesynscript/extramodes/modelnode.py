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
            
            
    @Scripting.printable
    def run(self, code):
        right_mode = None
        for mode in self.__modes:
            if mode.test(code):
                right_mode = mode
                break
        
        if right_mode:
            expr_str, display_str = right_mode.translate(code)
            self.root_node.stream_manager.write(f'''
WaveSyn:
The mode of the code is recognized as {right_mode.info.name}. 
The actual code executed is listed as follows:
''', 'TIP') # To Do: The output is stored in ...
            self.root_node.lang_center.wavesynscript.display_and_eval(expr_str, display_str)
        else:
            raise TypeError('The mode of the code is unrecognizable.')