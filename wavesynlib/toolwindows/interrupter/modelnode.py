# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26 10:42:50 2016

@author: Feng-cong Li
"""

from __future__ import print_function, division, unicode_literals

from wavesynlib.languagecenter.wavesynscript import ModelNode
from wavesynlib import status

import six.moves._thread as thread
import threading
import subprocess as sp

from os.path import abspath, dirname, join
import inspect

import json


_is_alive = threading.Event()


def get_my_dir():
    return abspath(dirname(inspect.getfile(inspect.currentframe())))


def listener(p):    
    while True:
        command_json = p.stdout.readline()
        command = json.loads(command_json)
        if command['type'] == 'command':
            if command['command'] == 'exit':
                break
            elif command['command'] == 'interrupt_main_thread':
                if status.is_busy():
                    thread.interrupt_main()
    _is_alive.set()


class InterrupterNode(ModelNode):
    def __init__(self, *args, **kwargs):
        ModelNode.__init__(self, *args, **kwargs)
        winpath = join(get_my_dir(), 'interrupter.py')
        p = sp.Popen(['python', '-u', winpath], stdout=sp.PIPE, stdin=sp.PIPE)
        thread.start_new_thread(listener, (p,))
        self.__proc = p
        
    def close(self):
        if not _is_alive.is_set():
            self.__proc.stdin.write('!\n')