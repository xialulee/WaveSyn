# Modelnode for WSSh
#
# Run ls:
# #M! ls
#
# Run ls and store the stdout and stderr in the returned dict (s for storage):
# #M!s ls
#
# Run notepad in new thread, and the thread object is returned (the thread object can be accessed through variable "_").
# #M!t notepad
#
# Assign the return value to variable "retobj"
# #M!|retobj= ls
#
# Store stdout & stderr and assign the returned dict to "retobj"
# #M!s|retobj= ls
#
# Using format string:
# should print 100
# a = 100
# #M!f printf "%s" {a}
# 
# Using quotes
# a = "123 456"
# #M!f printf "%s" "{a}"
# (should print "123 456")
# #M!f printf "%s" {a}
# (should print "123")
#
# Command substitution
# #M!t gvim $(which test.py)
#
# Use Environ var and Command substitution in strings:
# #M! printf "%s" "--$(which python)--"
# #M! printf "%s" "---- $(which $(echo python)) ----"
# #M! printf "%s" "--$PATH--"
# Use $$ as escape of $:
# #M! printf "%s" "$$(which python)"
# (SHould print "$(which python)")

from __future__ import annotations

from typing import Tuple

import locale
import subprocess
import sys
import re
import io
from ..basemode import ModeInfo, BaseMode
from wavesynlib.languagecenter.wavesynscript import ModelNode, Scripting, WaveSynScriptAPI, ScriptCode, code_printer
from .execute import run

_encoding = locale.getpreferredencoding()



def _get_leading_blanks(s):
    t = s.lstrip()
    d = len(s) - len(t)
    return s[:d]



class WSSh(ModelNode, BaseMode):
    _MODE_PREFIX = "#M!"
    _PREFIX_ARG_PATTERN = re.compile(
        """\
(?P<exec_mode>[stnf]*)      
# s for storage; 
# t for threading; 
# n for not displaying;
# f for using f-str as command.
(?:\\[(?P<shell>.*)\\])?
# Shell selection.
# Default shell will be used if not specified.
# [uow]: Select Ubuntu-on-Windows bash as shell.
(?:\\((?P<stdin_var>.*)\\))?  
# the var name of which the content will be written into stdin.
(?:\\|(?P<return_var>\\w+)=)?
# the var name of the run's (or run.new_thread_run's) return value."""
        , re.VERBOSE)


    @classmethod
    def get_prefix(cls):
        return cls._MODE_PREFIX


    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        with self.attribute_lock:
            self.info = ModeInfo("wssh", False, self)
            self.result = {"stdout": "", "stderr": ""}


    def __run_process(self, command, input) -> Tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        returncode = run(command, stdout=stdout, stderr=stderr)
        stdout.seek(0)
        stderr.seek(0)
        return returncode, stdout.read(), stderr.read()


    def test(self, code):
        return \
            self.info \
                if code.lstrip().startswith(self._MODE_PREFIX) else \
            False


    @WaveSynScriptAPI(thread_safe=True)
    def run(self, command, display=True, input=None, store=False):
        # Todo: 
        # Support store stdout & stderr;
        # Support run in thread.
        result = {
            'returncode': None, 
            'stdout': None, 
            'stderr': None
        }
        self.result['stdout'] = ''
        self.result['stderr'] = ''
        if isinstance(input, str):
            input = input.encode(_encoding)
        returncode, stdout, stderr = self.__run_process(command, input=input)
        result['returncode'] = returncode
        if store:
            result['stdout'] = stdout
            result['stderr'] = stderr
        if display:
            print(stdout)
            print(stderr, file=sys.stderr)
        return result


    def _arg_parse(self, code):
        # Todo: #M! default;
        prefix_args, code = self._split_code(code)
        match_obj = re.match(self._PREFIX_ARG_PATTERN, prefix_args)
        stdin_var = match_obj['stdin_var']
        exec_mode = match_obj['exec_mode']
        shell_name = match_obj['shell']
        retvar = match_obj['return_var']
        arg_dict = {'command': code}
        if stdin_var:
            arg_dict['input'] = ScriptCode(stdin_var)
        if 's' in exec_mode:
            arg_dict['store'] = True
        if 't' in exec_mode:
            # However, "thread" is not an argument.
            # It serves as a flag indicating that
            # the command will run in a new thread. 
            arg_dict['thread'] = True
        if 'n' in exec_mode:
            arg_dict['display'] = False
        if 'f' in exec_mode:
            arg_dict['command'] = ScriptCode('f' + repr(code))
        if retvar:
            arg_dict['retvar'] = retvar
        if shell_name == 'uow':
            command_prefix = 'f' if 'f' in exec_mode else ''
            arg_dict['command'] = ScriptCode(
                f"['bash', '-c', {command_prefix}{repr(code)}]")
        return arg_dict
    

    def translate(self, code, verbose=None):
        leading_blanks = _get_leading_blanks(code)
        code = code.lstrip()
        arg_dict = self._arg_parse(code)
        # "thread" is a flag rather than an arg.
        is_thread = arg_dict.pop("thread", False)
        if is_thread:
            thread_code = ".new_thread_run"
        else:
            thread_code = ""
        retvar = arg_dict.pop("retvar", "")
        arg_str = Scripting.convert_args_to_str(**arg_dict)
        result = (
            f"{leading_blanks}{self.node_path}.run{thread_code}({arg_str})")
        if retvar:
            result = f"{retvar} = {result}"
        if verbose:
            write = self.root_node.stream_manager.write
            write("The translated code is given as follows:\n", "TIP")
            write(f"{result}\n", "HISTORY")
            if arg_dict.get("store", ""):
                write(
                    f"""\
'store=True' indicating that the contents of stdout & stderr are stored in the return value. """, 
                    'TIP'
                ) 
        return result


    def execute(self, code):
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