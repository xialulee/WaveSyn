from __future__ import annotations

import re
import sys
import importlib
from typing import Any, Tuple, List, Final 

from wavesynlib.languagecenter.wavesynscript import ModelNode, Scripting, ScriptCode, code_printer
from .pattern import command_pattern, arg_pattern
from ..basemode import BaseMode, ModeInfo



def _get_leading_blanks(s: str) -> str:
    t = s.lstrip()
    d = len(s) - len(t)
    return s[:d]


def command_parse(command: str) -> Tuple[str, List[str]]:
    command = command.lstrip()
    m = re.match(command_pattern, command)
    if not m:
        raise SyntaxError("Invalid command.")
    name = m[0]
    command = command[len(name):]
        
    left = command
    args = []
    while True:
        left = left.lstrip()
        m = re.match(arg_pattern, left)
        if m is None:
            break
        else:
            arg = m[0]
            args.append(arg)
            left = left[len(arg):]
    return name, args



class Magic(ModelNode, BaseMode):
    _MODE_PREFIX: Final[str] = "#M%"
    _PREFIX_ARG_PATTERN: Final[re.Pattern] = \
        re.compile("(?P<exec_mode>[f]*)", re.VERBOSE)

    @classmethod
    def get_prefix(cls) -> str:
        return cls._MODE_PREFIX

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        with self.attribute_lock:
            self.info = ModeInfo("magic", multiline=False, mode_object=self)

    def test(self, code: str) -> ModeInfo | None:
        if code.lstrip().startswith(self._MODE_PREFIX):
            return self.info
        else:
            return None

    def run(self, command: str):
        name, args = command_parse(command)
        args.insert(0, name)
        mod = importlib.import_module(
            f".commands.{name}", 
            package=self.__module__.rsplit(sep=".", maxsplit=1)[0])
        main = mod.main
        return main(self.root_node, args)

    def _arg_parse(self, code: str) -> dict[str, str | ScriptCode]:
        prefix_args, code = self._split_code(code)
        match_obj = re.match(self._PREFIX_ARG_PATTERN, prefix_args)
        if not match_obj:
            raise SyntaxError("Invalid arguments.")
        exec_mode = match_obj["exec_mode"]
        result: dict[str, str | ScriptCode] = {
            "command": code
        }
        if "f" in exec_mode:
            result["command"] = ScriptCode("f" + repr(code))
        return result

    def translate(self, code: str, verbose: bool = False) -> str:
        leading_blanks = _get_leading_blanks(code)
        code = code.lstrip()
        arg_dict = self._arg_parse(code)
        arg_str = Scripting.convert_args_to_str(**arg_dict)
        result = f"{leading_blanks}{self.node_path}.run({arg_str})"
        if verbose:
            write = self.root_node.stream_manager.write
            write("The translated code is given as follows\n", "TIP")
            write(f"{result}\n", "HISTORY")
        return result

    def execute(self, code: str) -> Any:
        code = code.lstrip()
        try:
            arg_dict = self._arg_parse(code)
        except SyntaxError as err:
            print()
            print(err, file=sys.stderr)
            return
        with code_printer(True):
            result = self.run(**arg_dict)
        return result
