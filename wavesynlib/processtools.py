# -*- coding: utf-8 -*-
"""
Created on Wed Feb 22 14:10:51 2017

@author: Feng-cong Li
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import six
from six.moves import cStringIO as StringIO
import socket
import json
from subprocess import Popen, PIPE


from wavesynlib.languagecenter.wavesynscript import ModelNode, NodeDict
from wavesynlib.languagecenter.designpatterns import Singleton
from wavesynlib.languagecenter import datatypes


class ProcessNode(ModelNode):
    def __init__(self, *args, **kwargs):
        self.__file_path = kwargs.pop('file_path')
        self.__parameters = kwargs.pop('parameters')
        super(ProcessNode, self).__init__(*args, **kwargs)
        
        
@six.add_metaclass(Singleton)
class ProcessDict(NodeDict):
    def __init__(self, *args, **kwargs):
        super(ProcessDict, self).__init__(*args, **kwargs)
        
        
    def create(self, commandline):
        p = Popen(commandline, stdout=PIPE, stdin=PIPE)
        self.__listen(p)
        return self.add(p)
        
        
    def __listen(self, process):
        @self.root_node.thread_manager.new_thread_do
        def read_stdout():
            while True:
                command = p.stdout.readline()
                command = json.loads(command)
                slot = datatypes.CommandSlot(
                    source='local', 
                    node_list=command['node_list'],
                    method_name=command['method_name'],
                    args=command['args'],
                    kwargs=command['kwargs'])
                if not command:
                    break
                self.root_node.command_queue.put(slot)