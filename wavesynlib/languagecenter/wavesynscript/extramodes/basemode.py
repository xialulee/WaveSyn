from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Tuple



class ModeInfo:
    __slot__ = ("name", "multiline", "mode_object")
    
    def __init__(self, name, multiline, mode_object):
        self.name = name
        self.multiline = multiline
        self.mode_object = mode_object
        
        
    
class CodeInfo:
    __slot__ = ("mode_info", "code")



class BaseMode(ABC):
    @classmethod
    @abstractmethod
    def get_prefix(cls) -> str:
        raise NotImplementedError

    @abstractmethod
    def run(self, code: str):
        raise NotImplementedError

    @abstractmethod
    def test(self, code: str) -> ModeInfo | None:
        raise NotImplementedError

    @abstractmethod
    def translate(self, code: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def execute(self, code: str):
        raise NotImplementedError

    def _split_code(self, code: str) -> Tuple[str, str]:
        splited = code.split(maxsplit=1)
        if len(splited) < 2:
            raise SyntaxError("Mode prefix and code should be splited by blank.")
        prefix, code = splited
        return prefix[len(self.get_prefix()):], code


