# -*- coding: utf-8 -*-
"""
Created on Sat Sep 28 01:13:49 2019

@author: Feng-cong Li
"""
from __future__ import annotations

from typing import Callable, Iterable, Mapping

from io import IOBase
from pathlib import PurePath

from wavesynlib.languagecenter.wavesynscript import Scripting, ModelNode, WaveSynScriptAPI
from wavesynlib.languagecenter import datatypes
from wavesynlib.fileutils.tar import TarFileManager



class FileUtils(ModelNode):
    def __init__(self, *args, **kwargs):
        ModelNode.__init__(self, *args, **kwargs)                
        self.pdf_files = ModelNode(
            is_lazy=True, 
            module_name='wavesynlib.interfaces.pdf.modelnode', 
            class_name='PDFFileManager')
        self.touchstone_files = ModelNode(
            is_lazy=True, 
            module_name='wavesynlib.interfaces.devcomm.touchstone.modelnode', 
            class_name='TouchstoneFileManager')
        self.tar_files = ModelNode(is_lazy=True, class_object=TarFileManager)
        
        
    @WaveSynScriptAPI(thread_safe=True)
    def calc_hash(self, 
            file:      datatypes.ArgOpenFile | str | IOBase, 
            algorithm: str, 
            on_finish: Iterable[Callable[[str], None] | str] | None = None
        ) -> str:
        '''\
Calculate the hash code of a given file.

return: the hash code of the given file. 

file: the path of the given file or a stream object.
algorithm: the name of the hash algorithm.
'''
        from wavesynlib.fileutils import calc_hash

        command_dict: Mapping[str, Callable[[str], None]] = {
            "display": print,
            "print":   print
        }

        def do_on_finish(code: str) -> None:
            if on_finish:
                for command in on_finish:
                    if isinstance(command, str):
                        command = command_dict[command]
                    elif callable(command):
                        pass
                    else:
                        raise TypeError("Elements of on_finish should be command strings or callable objects.")
                    command(code)
        
        file = self.root_node.gui.dialogs.constant_handler_ASK_OPEN_FILENAME(
                file, 
                filetype=[('All Files', '*.*')])
                
        if isinstance(file, (str, PurePath)):
            with open(file, 'rb') as fileobj:
                result = calc_hash(fileobj, algorithm) 
                do_on_finish(result)
                return result
        elif isinstance(file, IOBase):
            result = calc_hash(file, algorithm) 
            do_on_finish(result)
            return result
        else:
            raise TypeError("Type of file is unsupported.")
