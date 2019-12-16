# -*- coding: utf-8 -*-
"""
Created on Sat Aug 27 23:09:18 2016

@author: Feng-cong Li
"""
import sys
import traceback
import subprocess
import locale

from wavesynlib.status import busy_doing

from wavesynlib.languagecenter.wavesynscript import (
    ModelNode, Constants, Scripting)
from .extramodes.modelnode import ExtraModesNode



def _remove_line_continuation(code):
    rstrip_code = code.rstrip()
    if rstrip_code.endswith("\\"):
        return rstrip_code[:-1], True
    else:
        return code, False



class WaveSynScriptNode(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.constants = Constants
        self.extra_modes = ExtraModesNode()
        self.__display_language = "python"
        self.__code_list = []
        self.__prev_line_continuation = False


    @property
    def display_language(self):
        return self.__display_language


    @Scripting.printable
    def set_display_language(self, language):
        language = language.lower()
        if language in ("py", "python"):
            self.__display_language = "python"
        elif language == "hy":
            self.__display_language = "hy"
        else:
            raise ValueError(f"Language {language} not supported.")


    def _translate_code_list(self, code_list=None):
        if code_list is None:
            code_list = self.__code_list
        translate = self.extra_modes.translate
        for index, line in enumerate(code_list):
            try:
                code_list[index] = translate(line)[0]
            except TypeError:
                pass


    def feed(self, code):
        def do_nothing():
            pass
        code_list = self.__code_list
        block_finished = False
        stripped_code = code.strip()
        if not stripped_code:
            # A blank line ends a block.
            self._translate_code_list()
            code = "\n".join(code_list)
            del code_list[:]
            block_finished = True
        stripped_code = code.strip()
        if not stripped_code:
            # Nothing meaningful input.
            return "EXECUTE", do_nothing
        first_sym, last_sym = stripped_code[0], stripped_code[-1]
        if code_list or \
                    last_sym in (":", "\\") or \
                    (first_sym in ("@",) and not block_finished):
            # A new block, decorated func/class and multiline being created.
            # Store the lines of code in self.__code_list,
            # until a blank line appears.
            code = _remove_line_continuation(code)[0]
            # Remove the line continuation if it exists.
            # We can still know wheter line continuation exists in the original code
            # by reading the last_sym variable.
            if self.__prev_line_continuation:
                # The previous line ends up with a line continuation.
                # Join the current line with the previous line, instead of
                # making a new line.
                code_list[-1] = f"{code_list[-1]}{code}"
            else:
                code_list.append(code)
            self.__prev_line_continuation = last_sym == "\\"
            return "APPEND", do_nothing
        else:
            # One-line code
            def execute():
                nonlocal code
                try:
                    code = self.extra_modes.translate(code, verbose=True)[0]
                except TypeError:
                    pass
                return self.execute(code)
            return "EXECUTE", execute


    def eval(self, expr):
        root_node = self.root_node
        with root_node.exec_thread_lock:
            try:
                with busy_doing:
                    ret = eval(expr, Scripting.namespaces['globals'], Scripting.namespaces['locals'])
            except KeyboardInterrupt:
                root_node.stream_manager.write('The mission has been aborted.\n', 'TIP')
            Scripting.namespaces['locals']['_']  = ret
            return ret
            

    def display_and_eval(self, expr, display=None):
        root_node = self.root_node
        if display is None:
            display = expr
        with root_node.exec_thread_lock:
            root_node.stream_manager.write(display+'\n', 'HISTORY')               
            ret = self.eval(expr)
            if ret is not None:
                root_node.stream_manager.write(str(ret)+'\n', 'RETVAL', extras={'obj':ret})
            return ret    


    def execute(self, code):
        root_node = self.root_node

        with root_node.exec_thread_lock:
            ret = None
            try:
                try:
                    with busy_doing:
                        ret = self.eval(code)
                except SyntaxError:
                    with busy_doing:
                        try:
                            exec(code, Scripting.namespaces['globals'], Scripting.namespaces['locals'])
                        except KeyboardInterrupt:
                            root_node.stream_manager.write('WaveSyn: The mission has been aborted.\n', 'TIP')
            except SystemExit:
                root_node._on_exit()
            except:
                traceback.print_exc()
            return ret
