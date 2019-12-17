from abc import ABC, abstractmethod



class ModeInfo:
    __slot__ = ('name', 'multiline', 'mode_object')
    
    def __init__(self, name, multiline, mode_object):
        self.name = name
        self.multiline = multiline
        self.mode_object = mode_object
        
        
    
class CodeInfo:
    __slot__ = ('mode_info', 'code')



class BaseMode(ABC):
    @classmethod
    @abstractmethod
    def get_prefix(cls):
        pass


    @abstractmethod
    def run(self, code):
        pass


    @abstractmethod
    def test(self, code):
        pass


    @abstractmethod
    def translate(self, code):
        pass


    @abstractmethod
    def execute(self, code):
        pass


    def _split_code(self, code):
        splited = code.split(maxsplit=1)
        if len(splited) < 2:
            raise SyntaxError("Mode prefix and code should be splited by blank.")
        prefix, code = splited
        return prefix[len(self.get_prefix()):], code


