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


class WaveSynScriptNode(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.constants = Constants
        self.extra_modes = ExtraModesNode()
        self.__display_language = "python"


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
            

    def display_and_eval(self, expr):
        root_node = self.root_node
        with root_node.exec_thread_lock:
            root_node.stream_manager.write(expr+'\n', 'HISTORY')               
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


    def hy_display_and_eval(self, hystr, expr):
        root_node = self.root_node
        with root_node.exec_thread_lock:
            root_node.stream_manager.write(hystr+"\n", "HISTORY")
            ret = expr()
            if ret is not None:
                root_node.stream_manager.write(str(ret)+"\n", "RETVAL", extras={"obj":ret})
            return ret
