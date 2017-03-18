# -*- coding: utf-8 -*-
"""
Created on Wed Feb 22 14:10:51 2017

@author: Feng-cong Li
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
from subprocess import Popen, PIPE


from wavesynlib.languagecenter.wavesynscript import ModelNode, NodeDict
from wavesynlib.languagecenter import datatypes


class ProcessNode(ModelNode):
    def __init__(self, *args, **kwargs):
        self.__executable = kwargs.pop('executable')
        self.__parameters = kwargs.pop('parameters')
        commandline = []
        commandline.append(self.__executable)
        commandline.extend(self.__parameters)
        self.__pipes = Popen(commandline, stdout=PIPE, stdin=PIPE)
        super(ProcessNode, self).__init__(*args, **kwargs)
        
        
    def run(self):
        p = self.__pipes
        @self.root_node.thread_manager.new_thread_do
        def read_stdout():
            while True:
                command = p.stdout.readline()
                
                if not command:
                    # The pipe closed. 
                    break
                
                command = json.loads(command)
                slot = datatypes.CommandSlot(
                    source='local', 
                    node_list=command['node_list'],
                    method_name=command['method_name'],
                    args=command['args'],
                    kwargs=command['kwargs'])                
                self.root_node.command_queue.put(slot)
                    
        
        
class ProcessDict(NodeDict):
    def __init__(self, *args, **kwargs):
        NodeDict.__init__(self, *args, **kwargs)
        
        
    def create(self, executable, parameters):        
        p = ProcessNode(executable=executable, parameters=parameters)
        p.run()
        return self.add(p)
        
        
    def add(self, node):
        self[id(node)] = node
        return id(node)        
        
        

if __name__ == '__main__':
    # For testing
    import time
    for k in range(10):
        print('{"a":"b"}')
        time.sleep(2)
